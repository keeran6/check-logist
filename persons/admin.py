# -*- coding: utf-8 -*-
'''
Created on 25.06.2012

@author: Admin
'''
from django.contrib import admin
from persons.models import Person

admin.site.register(Person)