# -*- coding: utf-8 -*-
'''
Created on 25.06.2012

@author: Admin
'''
from django.contrib import admin
from persons.models import Person, Customer, Broker, Dispatcher, Executor
from django.contrib.admin import ModelAdmin

class PersonAdmin(ModelAdmin):
    readonly_fields = ('total_debt', 'appearance_date',)
    
class CustomerAdmin(PersonAdmin):
    exclude = ('birthday', 'name', 'address',)

class ExecutorAdmin(PersonAdmin):
    readonly_fields = ('total_debt', 'appearance_date', 'last_contact')
    list_display = ('name', 'free_datetime', 'current_order', 'phone', 'address', 'birthday', 'total_debt',)
    list_filter = ('branch',)

admin.site.register(Person, PersonAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Broker, PersonAdmin)
admin.site.register(Dispatcher, PersonAdmin)
admin.site.register(Executor, ExecutorAdmin)