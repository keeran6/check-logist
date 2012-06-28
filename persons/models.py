# -*- coding: utf-8 -*-
from django.db import models
from prices.models import Branch
from datetime import datetime

class Person(models.Model):
    class Meta:
        verbose_name = 'лицо'
        verbose_name_plural = 'лица'
        ordering = ('surname', 'name')
    def __unicode__(self):
        return u' '.join((self.surname, self.name))
    surname         = models.CharField(max_length=128, verbose_name='фамилия (название)', blank=True)
    name            = models.CharField(max_length=128, verbose_name='имя', blank=True)
    phone           = models.CharField(max_length=128, verbose_name='телефон', blank=True)
    birthday        = models.DateField(verbose_name='дата рождения', null=True, blank=True)
    address         = models.CharField(max_length=256, verbose_name='адрес', blank=True)
    total_debt      = models.FloatField(default=0.0, verbose_name='задолженность', null=False, blank=True)
    appearance_date = models.DateField(verbose_name='появился', null=True, blank=True, default=datetime.today)
    branch          = models.ForeignKey(Branch, verbose_name='филиал', null=True, blank=True)

class Customer(Person):
    class Meta:
        verbose_name = 'заказчик'
        verbose_name_plural = 'заказчики'

class Broker(Person):
    class Meta:
        verbose_name = 'посредник'
        verbose_name_plural = 'посредники'

class Dispatcher(Person):
    class Meta:
        verbose_name = 'диспетчер'
        verbose_name_plural = 'диспетчеры'
        
class Executor(Person):
    class Meta:
        verbose_name = 'исполнитель'
        verbose_name_plural = 'исполнители'
    