# -*- coding: utf-8 -*-
'''
Created on 25.06.2012

@author: Admin
'''
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from orders.models import Work, Order, ExtendedPlan, ExtendedOrder,\
    ExtendedFinishedOrder
from django.http import HttpResponseRedirect
from django.core import urlresolvers
from orders.forms import OrderForm, WorkForm
from persons.models import Dispatcher
from prices.models import Price, PaymentMethod
from functools import update_wrapper
from django.conf.urls import patterns, url


class OrderWorkInline(admin.TabularInline):
    form = WorkForm
    model = Work
    extra = 1
    max_num = 10
    
class OrderAdmin(ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (('dispatcher', 'customer', 'broker', 'code'),
                      ('branch', 'service', 'payment_method'),
                      ('datetime', 'executors_required'),
                      'contacts', 'start', 'finish', 'cargo', 'description',)
        }),
        ('SMS', {
            'fields': ('sms', 'cut_sms')
        }),
    )
    def __init__(self, model, admin_site):
        if model == Order:
            self.list_display = []
            self.list_filter = []
        ModelAdmin.__init__(self, model, admin_site)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        return ModelAdmin.change_view(self, request, object_id, form_url=form_url, extra_context={
                                                                                                  'prices': Price.objects.all().values(),
                                                                                                  'payment_methods': PaymentMethod.objects.all().values()
                                                                                                  })
    form = OrderForm
    inlines = [OrderWorkInline]
    def get_form(self, request, obj=None, **kwargs):
        if request.method == 'POST' and obj is None:
            try:
                request.POST['dispatcher'] = Dispatcher.objects.get(name__iexact=u' '.join((request.user.last_name, request.user.first_name)))
            except:
                pass
        return ModelAdmin.get_form(self, request, obj=obj, **kwargs)
    def response_add(self, request, obj, post_url_continue='../%s/'):
        messages.add_message(request, messages.WARNING, u'Заказ добавлен! Тщательно проверьте его на наличие ошибок.')
        return HttpResponseRedirect(urlresolvers.reverse('admin:orders_order_change', args=(obj.id,)))
    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect(urlresolvers.reverse('admin:orders_extendedorder_changelist'))


class ExtendedOrderAdmin(ModelAdmin):
    list_display = ('datetime', 'customer', 'branch', 'executors_accepted', 'executors_required', 'executors_verified', 'payment_method', 'quantity', 'total', 'start',)
    list_filter = ('branch', 'payment_method', 'dispatcher')
    ordering = ('-datetime', 'id')
    date_hierarchy = 'datetime'
    search_fields = ['customer__name', 'branch__name', 'start', 'payment_method__name', 'dispatcher__name']
    list_select_related = True
    
    def __init__(self, model, admin_site):
        self.order_admin = OrderAdmin(Order, admin_site)
        ModelAdmin.__init__(self, model, admin_site)

    def change_view(self, request, object_id, form_url='', extra_context=None):\
        return self.order_admin.change_view(request, object_id, form_url, extra_context)
    
    def delete_view(self, request, object_id, extra_context=None):
        return self.order_admin.delete_view(request, object_id, extra_context)
    
    def add_view(self, request, form_url='', extra_context=None):
        return self.order_admin.add_view(request, form_url, extra_context)
    
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        info = self.model._meta.app_label, 'order'
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
        return super(ExtendedOrderAdmin, self).get_urls() + urlpatterns


class WorkAdmin(ModelAdmin):
    list_display = ('order', 'executor', 'fee_through', 'quantity', 'total', 'executor_sum', 'executor_balance')
    ordering = ('-order__datetime', 'id')
    search_fields = ['order__customer__name', 'executor__name']
    list_select_related = True
    #date_hierarchy = 'order__datetime'

admin.site.register(ExtendedPlan, ExtendedOrderAdmin)
admin.site.register(ExtendedFinishedOrder, ExtendedOrderAdmin)
admin.site.register(ExtendedOrder, ExtendedOrderAdmin)
admin.site.register(Work, WorkAdmin)
