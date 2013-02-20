# -*- coding: utf-8 -*-
'''
Created on 25.06.2012

@author: Admin
'''
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from cash.models import Income, Expense, MoneyTransfer

class MoneyOperationAdmin(ModelAdmin):
    list_display = ('date', 'person', 'total', 'note', 'settlement_item')
    ordering = ('-date', 'id')
    date_hierarchy = 'date'
    search_fields = ['person__name', 'note',]

class MoneyTransferAdmin(ModelAdmin):
    list_display = ('date', 'from_person', 'to_person', 'total', 'note',)
    ordering = ('-date', 'id')
    date_hierarchy = 'date'
    search_fields = ['from_person__name', 'to_person__name', 'note',]


admin.site.register(Income, MoneyOperationAdmin)
admin.site.register(Expense, MoneyOperationAdmin)
admin.site.register(MoneyTransfer, MoneyTransferAdmin)
