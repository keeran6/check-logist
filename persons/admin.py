# -*- coding: utf-8 -*-
'''
Created on 25.06.2012

@author: Admin
'''
from django.contrib import admin
from persons.models import Person, Customer, Broker, Dispatcher, Executor, ExtendedExecutor
from django.contrib.admin import ModelAdmin
from persons.forms import ExecutorForm
from orders.models import Work
from django.contrib import messages
from django.contrib.auth.admin import csrf_protect_m
from django.http import HttpResponseRedirect
from django.core import urlresolvers
from django.db import transaction
from datetime import datetime

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
    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect(urlresolvers.reverse('admin:persons_extendedexecutor_changelist'))
    
    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method != 'POST':
            executor = Executor.objects.get(pk=object_id)
            delay = (datetime.now() - executor.last_contact).seconds / 60
            if delay < 60:
                messages.add_message(request, messages.INFO if delay > 15 else messages.ERROR, 'Исполнитель обзвонен %s минут назад' % delay)
        return PersonAdmin.change_view(self, request, object_id, form_url=form_url, extra_context=extra_context)
    
class ExtendedExecutorAdmin(PersonAdmin):
    list_display = ('name', 'free_datetime', 'current_order', 'current_order_accepted', 'note', 'phone', 'address', 'total_debt',)
    list_filter = ('branch', 'current_order_accepted')
    search_fields = ['name', 'current_order__customer__name', 'note', 'phone', 'address']
    ordering = ('-current_order_accepted', 'free_datetime', 'current_order__id')
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
    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, request, object_id, form_url='', extra_context=None):\
        return HttpResponseRedirect(urlresolvers.reverse('admin:persons_executor_change', args=(object_id,)))
    
    @csrf_protect_m
    @transaction.commit_on_success
    def delete_view(self, request, object_id, extra_context=None):
        return HttpResponseRedirect(urlresolvers.reverse('admin:persons_executor_delete', args=(object_id,)))
    
    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        return HttpResponseRedirect(urlresolvers.reverse('admin:persons_executor_add'))
    
admin.site.register(Person, PersonAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Broker, PersonAdmin)
admin.site.register(Dispatcher, PersonAdmin)
admin.site.register(Executor, ExecutorAdmin)
admin.site.register(ExtendedExecutor, ExtendedExecutorAdmin)