# -*- coding: utf-8 -*-
'''
Created on 25.06.2012

@author: Admin
'''
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from orders.models import Work, Order, Plan
from django.contrib.admin.options import csrf_protect_m
from django.db import transaction
from django.http import HttpResponseRedirect
from django.core import urlresolvers
from orders.forms import OrderForm
from persons.models import Dispatcher

class OrderWorkInline(admin.TabularInline):
    model = Work
    extra = 10
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
    form = OrderForm
    save_on_top = True
    inlines = [OrderWorkInline]
    list_display = ('customer', 'datetime',)
    list_filter = ('branch',)
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

class PlanAdmin(OrderAdmin):
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
    
admin.site.register(Order, OrderAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Work)
