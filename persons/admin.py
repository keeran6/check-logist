# -*- coding: utf-8 -*-
'''
Created on 25.06.2012

@author: Admin
'''
from django.contrib import admin
from persons.models import Person, Customer, Broker, Dispatcher, Executor, ExtendedExecutor,\
    Debt
from django.contrib.admin import ModelAdmin
from persons.forms import ExecutorForm
from orders.models import Work
from django.contrib import messages
from django.contrib.auth.admin import csrf_protect_m
from datetime import datetime, timedelta
from django.contrib.admin.filters import SimpleListFilter
from hephaestus import settings
from django.db.models.aggregates import Min, Max, Sum
from functools import update_wrapper
from django.conf.urls import patterns, url

class PersonAdmin(ModelAdmin):
    readonly_fields = ('total_debt', 'appearance_date',)
    list_display = ('name', 'phone', 'total_debt', 'branch')
    list_filter = ('branch',)
    search_fields = ['name', 'phone', 'branch__name']
    ordering = ('name',)
        
    
class CustomerAdmin(PersonAdmin):
    exclude = ('birthday', 'address',)
    
class ExecutorAdmin(PersonAdmin):
    form = ExecutorForm
    readonly_fields = ('total_debt', 'appearance_date', 'last_contact',)
        
class ExtendedExecutorAdmin(PersonAdmin):
    list_display = ('name', 'category', 'free_datetime', 'current_order', 'current_order_accepted', 'note', 'phone', 'address', 'total_debt',)
    list_filter = ('branch', 'current_order_accepted')
    search_fields = ['name', 'current_order__customer__name', 'note', 'phone', 'address']
    #list_editable = ('current_order',)
    ordering = ('-current_order_accepted', 'current_order__id', 'category', 'free_datetime')

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        info = self.model._meta.app_label, 'executor'
        urlpatterns = patterns('',
            url(r'^$',
                wrap(self.changelist_view),
                name='%s_%s_changelist' % info),
            url(r'^add/$',
                wrap(self.add_view),
                name='%s_%s_add' % info),
            url(r'^(.+)/history/$',
                wrap(self.history_view),
                name='%s_%s_history' % info),
            url(r'^(.+)/delete/$',
                wrap(self.delete_view),
                name='%s_%s_delete' % info),
            url(r'^(.+)/$',
                wrap(self.change_view),
                name='%s_%s_change' % info),
        )
        return super(ExtendedExecutorAdmin, self).get_urls() + urlpatterns

    
    def __init__(self, model, admin_site):
        self.executor_admin = ExecutorAdmin(Executor, admin_site)
        return super(ExtendedExecutorAdmin, self).__init__(model, admin_site)
    
    def reject_order(self, request, queryset):
        for executor in queryset:
            Work.objects.filter(order=executor.current_order, executor=executor).delete()
        messages.add_message(request, messages.WARNING, 'Исполнители сняты с заказа! Дайте отбой исполнителям!')
    reject_order.short_description = 'Отбой по заказу'
    def accept_order(self, request, queryset):
        for executor in queryset:
            Work.objects.filter(order=executor.current_order, executor=executor).update(accepted=True)
        messages.add_message(request, messages.WARNING, 'Заказы помечены как подтвержденные исполнителями! Убедитесь, что они действительно подтвердили заказы!')
    accept_order.short_description = 'Исполнитель подтвердил заказ'
    def finish_order(self, request, queryset):
        for executor in queryset:
            Work.objects.filter(order=executor.current_order, executor=executor).update(finished=True)
        messages.add_message(request, messages.WARNING, 'Заказы помечены как завершенные исполнителями!')
    finish_order.short_description = 'Исполнитель завершил заказ'
    actions = [reject_order, accept_order, finish_order]
    

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method != 'POST':
            executor = Executor.objects.get(pk=object_id)
            delay = (datetime.now() - executor.last_contact).seconds / 60
            if delay < 60:
                messages.add_message(request, messages.INFO if delay > 15 else messages.ERROR, 'Исполнитель обзвонен %s минут назад' % delay)
        return self.executor_admin.change_view(request, object_id, form_url, extra_context)
    
    def delete_view(self, request, object_id, extra_context=None):
        return self.executor_admin.delete_view(request, object_id, extra_context)
    
    def add_view(self, request, form_url='', extra_context=None):
        return self.executor_admin.add_view(request, form_url, extra_context)
    
    
class HierarchyDateListFilter(SimpleListFilter):

    def lookups(self, request, model_admin):
        if not request.GET.has_key(self.parameter_name):
            years = Debt.objects.extra(select={'year': "year(date)"}).distinct().values_list('year', flat=True)
            return map(None, years, years)
        try:
            vals = []
            current = datetime.strptime(request.GET[self.parameter_name], '%Y')
            for month in xrange(1, 13):
                current = current.replace(month=month)
                string_current = current.strftime('%m.%Y')
                vals.append((string_current, string_current))
            return tuple(vals)
        except:
            try:
                now = datetime.strptime(request.GET[self.parameter_name], '%m.%Y')
                current = now.replace(day=1)
                vals = []
                while current.month == now.month:
                    string_current = current.strftime(settings.DATE_INPUT_FORMATS[0])
                    vals.append((string_current, string_current))
                    current += timedelta(days=1)
                return tuple(vals)
            except:
                try:
                    now = datetime.strptime(request.GET[self.parameter_name], '%d.%m.%Y')
                    current = now.replace(day=1)
                    vals = []
                    while current.month == now.month:
                        string_current = current.strftime(settings.DATE_INPUT_FORMATS[0])
                        vals.append((string_current, string_current))
                        current += timedelta(days=1)
                    return tuple(vals)
                except:
                    years = Debt.objects.extra(select={'year': "year(date)"}).distinct().values_list('year', flat=True)
                    return map(None, years, years)
    
    def queryset(self, request, queryset):
        if self.value() is not None:
            try:
                val = datetime.strptime(self.value(), '%Y')
                val = val.replace(month=1, day=1)
                if self.parameter_name.endswith('lte'):
                    val = val.replace(year=val.year + 1)
            except:
                try:
                    val = datetime.strptime(self.value(), '%m.%Y')
                    val = val.replace(day=1)
                    if self.parameter_name.endswith('lte'):
                        val = val.replace(month=val.month + 1)
                except:
                    try:
                        val = datetime.strptime(self.value(), '%d.%m.%Y')
                    except:
                        return queryset
            return queryset.filter(**{self.parameter_name: val})
        return queryset

class GreaterThanOrEqualHierarchyDateListFilter(HierarchyDateListFilter):
    title = 'Не раньше'
    parameter_name = 'date__gte'
class LessThanOrEqualHierarchyDateListFilter(HierarchyDateListFilter):
    title = 'Не позже'
    parameter_name = 'date__lte'

class DebtAdmin(ModelAdmin):
    list_display = ('person', 'date', 'total', 'content_object', 'note')
    search_fields = ('person__name',)
    list_filter = [GreaterThanOrEqualHierarchyDateListFilter, LessThanOrEqualHierarchyDateListFilter]
    #date_hierarchy = 'date'
    ordering = ('-date', 'person')
    def get_list_display_links(self, request, list_display):
        return []
    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        response = ModelAdmin.changelist_view(self, request, extra_context=extra_context)
        queryset = response.context_data['cl'].get_query_set(request)
        queryset_len = queryset.count()
        if queryset_len == 0:
            response.context_data['person'] = None
        else:
            
            if request.GET.has_key('q'):
                try:
                    response.context_data['person'] = Person.objects.get(name__icontains=request.GET['q'])
                except:
                    response.context_data['person'] = None
                else:
                    min_date = queryset.aggregate(Min('date'))['date__min']
                    max_date = queryset.aggregate(Max('date'))['date__max']
                    start_debt = Debt.objects.filter(person=response.context_data['person'], date__lt=min_date).aggregate(Sum('total'))['total__sum'] or 0.0
                    final_debt = Debt.objects.filter(person=response.context_data['person'], date__lte=max_date).aggregate(Sum('total'))['total__sum'] or 0.0
                    response.context_data['start_debt'] = start_debt
                    response.context_data['final_debt'] = final_debt
                    response.context_data['period_debt'] = final_debt - start_debt
        return response
admin.site.register(Person, PersonAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Broker, PersonAdmin)
admin.site.register(Dispatcher, PersonAdmin)
admin.site.register(ExtendedExecutor, ExtendedExecutorAdmin)
admin.site.register(Debt, DebtAdmin)