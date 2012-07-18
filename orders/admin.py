# -*- coding: utf-8 -*-
'''
Created on 25.06.2012

@author: Admin
'''
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from orders.models import Work, Order, ExtendedPlan, ExtendedOrder,\
    ExtendedFinishedOrder
from django.contrib.admin.options import csrf_protect_m
from django.db import transaction
from django.http import HttpResponseRedirect
from django.core import urlresolvers
from orders.forms import OrderForm, WorkForm
from persons.models import Dispatcher
from prices.models import Price, PaymentMethod

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
    @csrf_protect_m
    @transaction.commit_on_success
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
        return HttpResponseRedirect(urlresolvers.reverse('admin:orders_order_change', args=(obj.id,)))#ModelAdmin.response_add(self, request, obj, post_url_continue=urlresolvers.reverse('admin:orders_order_add'))
    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect(urlresolvers.reverse('admin:orders_extendedorder_changelist'))


class ExtendedOrderAdmin(ModelAdmin):
    list_display = ('datetime', 'customer', 'branch', 'executors_accepted', 'executors_required', 'executors_verified', 'payment_method', 'quantity', 'total', 'start',)
    list_filter = ('branch', 'payment_method', 'dispatcher')
    ordering = ('-datetime', 'id')
    date_hierarchy = 'datetime'
    search_fields = ['customer__name', 'branch__name', 'start', 'payment_method__name', 'dispatcher__name']
    list_select_related = True
    @csrf_protect_m
    @transaction.commit_on_success
    def change_view(self, request, object_id, form_url='', extra_context=None):\
        return HttpResponseRedirect(urlresolvers.reverse('admin:orders_order_change', args=(object_id,)))
    
    @csrf_protect_m
    @transaction.commit_on_success
    def delete_view(self, request, object_id, extra_context=None):
        return HttpResponseRedirect(urlresolvers.reverse('admin:orders_order_delete', args=(object_id,)))
    
    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        return HttpResponseRedirect(urlresolvers.reverse('admin:orders_order_add'))

class WorkAdmin(ModelAdmin):
    list_display = ('order', 'executor', 'fee_through', 'quantity', 'total', 'executor_sum', 'executor_balance')
    ordering = ('-order__datetime', 'id')
    search_fields = ['order__customer__name', 'executor__name']
    list_select_related = True
    #date_hierarchy = 'order__datetime'

admin.site.register(Order, OrderAdmin)
admin.site.register(ExtendedOrder, ExtendedOrderAdmin)
admin.site.register(ExtendedPlan, ExtendedOrderAdmin)
admin.site.register(ExtendedFinishedOrder, ExtendedOrderAdmin)
admin.site.register(Work, WorkAdmin)
