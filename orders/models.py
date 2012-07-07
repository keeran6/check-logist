# -*- coding: utf-8 -*-
from django.db import models
from prices.models import Branch, PaymentMethod, Service
from django.db.models.base import Model
from persons.models import Executor

class Work(Model):
    '''
    Работа одного исполнителя
    '''
    class Meta:
        verbose_name = 'работа'
        verbose_name_plural = 'работы'
    quantity         = models.FloatField(default=0.0, verbose_name='количество')
    executor         = models.ForeignKey('persons.Executor', related_name='test', verbose_name='исполнитель')
    order            = models.ForeignKey('Order', verbose_name='заказ')
    accepted         = models.BooleanField(default=False, verbose_name='принято')
    fee_through      = models.ForeignKey('persons.Person', null=True, blank=True, verbose_name='расчет через')
    total            = models.FloatField(default=0.0, verbose_name='стоимость работы')
    broker_sum       = models.FloatField(default=0.0, verbose_name='комиссия')
    executor_sum     = models.FloatField(default=0.0, verbose_name='зарплата')
    executor_balance = models.FloatField(default=0.0, verbose_name='баланс исполнителя')
    customer_balance = models.FloatField(default=0.0, verbose_name='баланс клиента')
    broker_balance   = models.FloatField(default=0.0, verbose_name='баланс посредника')


class BaseOrder(Model):
    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        abstract = True
    def __unicode__(self):
        return ' '.join((unicode(self.customer), unicode(self.datetime)))
    dispatcher          = models.ForeignKey('persons.Dispatcher', verbose_name='диспетчер')
    broker              = models.ForeignKey('persons.Broker', null=True, blank=True, verbose_name='посредник')
    customer            = models.ForeignKey('persons.Customer', verbose_name='заказчик')
    code                = models.IntegerField(default=0, verbose_name='код')
    branch              = models.ForeignKey(Branch, verbose_name='филиал')
    service             = models.ForeignKey(Service, verbose_name='услуга')
    datetime            = models.DateTimeField(verbose_name='дата/время заказа')
    executors_required  = models.IntegerField(default=0, verbose_name='исполнителей требуется')
    start               = models.CharField(max_length=128, verbose_name='место начала')
    finish              = models.CharField(max_length=128, blank=True, verbose_name='место окончания')
    persons             = models.CharField(max_length=128, blank=True, verbose_name='контакты')
    description         = models.TextField(max_length=256, blank=True, verbose_name='описание')
    cargo               = models.CharField(max_length=64, verbose_name='груз')
    payment_method      = models.ForeignKey(PaymentMethod, verbose_name='способ оплаты')

class Order(BaseOrder):
    executors           = models.ManyToManyField(Executor, through='Work')

class Plan(BaseOrder):
    class Meta:
        verbose_name = 'план'
        verbose_name_plural = 'планы'
    executors_accepted  = models.IntegerField(default=0, verbose_name='приняли')
    executors_set       = models.IntegerField(default=0, verbose_name='отправлено')
        
    def save(self, force_insert=False, force_update=False, using=None):
        dict((field.attname, getattr(self, field.a)) for field in BaseOrder._meta.fields)
            
        BaseOrder.save(self, force_insert=force_insert, force_update=force_update, using=using) 