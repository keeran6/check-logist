# -*- coding: utf-8 -*-
'''
Created on 25.06.2012

@author: Admin
'''
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from orders.models import Work, Order, Plan
from django.contrib.admin.options import csrf_protect_m
from django.db import transaction
from django.http import HttpResponseRedirect
from django.core import urlresolvers

class OrderWorkInline(admin.TabularInline):
    model = Work
    extra = 10
    max_num = 10

class OrderAdmin(ModelAdmin):
    fields = (('dispatcher', 'customer', 'broker', 'code'),
              ('branch', 'service', 'payment_method'),
              ('datetime', 'executors_required'),
              'persons', 'start', 'finish', 'cargo', 'description'
    )
    inlines = [OrderWorkInline]
    list_display = ('customer', 'datetime',)
    list_filter = ('branch',)
    

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
