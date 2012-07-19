# -*- coding: utf-8 -*-
from django.db import models
from prices.models import Branch
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
class Person(models.Model):
    class Meta:
        verbose_name = 'лицо'
        verbose_name_plural = 'лица'
        ordering = ('name',)
    def __unicode__(self):
        return self.name
    name            = models.CharField(max_length=128, verbose_name='имя', blank=False, null=False)
    phone           = models.CharField(max_length=128, verbose_name='телефон', blank=True)
    birthday        = models.DateField(verbose_name='дата рождения', null=True, blank=True)
    address         = models.CharField(max_length=256, verbose_name='адрес', blank=True)
    total_debt      = models.FloatField(default=0.0, verbose_name='задолженность', null=False, blank=True)
    appearance_date = models.DateField(verbose_name='появился', null=True, blank=True, default=datetime.today)
    branch          = models.ForeignKey(Branch, verbose_name='филиал', null=True, blank=True)
    note            = models.CharField(max_length=128, verbose_name='примечание', blank=True)

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
        
class BaseExecutor(Person):
    class Meta:
        verbose_name = 'исполнитель'
        verbose_name_plural = 'исполнители'
        abstract = True
        ordering = ('name',)
    free_datetime = models.DateField(verbose_name='освободится', default=datetime.now, blank=True, null=True)
    last_contact  = models.DateTimeField(verbose_name='контакт', auto_now=True)
    category = models.IntegerField(verbose_name='К', default=0, help_text='0 - новенький, 1 - регулярно работает, 2 - редко работает, 3 - почти не работает, 4 - не работает')

class Executor(BaseExecutor):
    class Meta(BaseExecutor.Meta):
        ordering = ('name',)
    def get_current_order(self):
        return ExtendedExecutor.objects.get(pk=self).current_order
    current_order = property(get_current_order)
class ExtendedExecutor(BaseExecutor):
    class Meta(BaseExecutor.Meta):
        db_table = 'persons_executor_extended'
        verbose_name_plural = 'исполнители'
    def get_executor(self):
        return 
    current_order          = models.ForeignKey('orders.Order', verbose_name='текущий заказ', blank=True, null=True)
    current_order_accepted = models.NullBooleanField(verbose_name='принят', blank=True, null=True)
    def age(self):
        if self.birthday is None:
            return None
        return (datetime.now().date() - self.birthday).days / 365
    age.short_description = 'возраст'

class Debt(models.Model):
    class Meta:
        verbose_name = 'долг'
        verbose_name_plural = 'долги'
    person = models.ForeignKey(Person, verbose_name='лицо')
    date = models.DateField(verbose_name='дата')
    total = models.FloatField(verbose_name='сумма')
    note = models.CharField(max_length=128, verbose_name='примечание')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

class SamaraExecutorManager(models.Manager):
    def get_query_set(self):
        return super(SamaraExecutorManager, self).get_query_set().filter(branch_id=1)
    
class SamaraExecutor(ExtendedExecutor):
    class Meta:
        verbose_name = 'исполнитель'
        verbose_name_plural = 'исполнители - Самара'
        proxy = True
    objects = SamaraExecutorManager()