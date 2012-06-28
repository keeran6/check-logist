# -*- coding: utf-8 -*-
from django.db import models
from persons.models import Broker, Customer, Dispatcher, Executor, Person
from prices.models import Branch, PaymentMethod, Service
from django.db.models.base import Model

class Work(Model):
    '''
    Работа одного исполнителя
    '''
    class Meta:
        verbose_name = 'работа'
        verbose_name_plural = 'работы'
        ordering = ('-order__datetime', 'executor__name')
        app_label = 'orders'
    quantity         = models.FloatField(default=0.0, verbose_name='количество')
    executor         = models.ForeignKey(Executor, related_name='test', verbose_name='исполнитель')
    order            = models.ForeignKey('Order', verbose_name='заказ')
    accepted         = models.BooleanField(default=False, verbose_name='принято')
    fee_through      = models.ForeignKey(Person, null=True, blank=True, verbose_name='расчет через')
    total            = models.FloatField(default=0.0, verbose_name='стоимость работы')
    broker_sum       = models.FloatField(default=0.0, verbose_name='комиссия')
    executor_sum     = models.FloatField(default=0.0, verbose_name='зарплата')
    executor_balance = models.FloatField(default=0.0, verbose_name='баланс исполнителя')
    customer_balance = models.FloatField(default=0.0, verbose_name='баланс клиента')
    broker_balance   = models.FloatField(default=0.0, verbose_name='баланс посредника')

class Order(Model):
    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ('-datetime',)
        app_label = 'orders'
    def __unicode__(self):
        return ' '.join((unicode(self.customer), unicode(self.datetime)))
    dispatcher          = models.ForeignKey(Dispatcher, verbose_name='диспетчер')
    broker              = models.ForeignKey(Broker, null=True, blank=True, verbose_name='посредник')
    customer            = models.ForeignKey(Customer, verbose_name='заказчик')
    code                = models.IntegerField(default=0, verbose_name='код')
    branch              = models.ForeignKey(Branch, verbose_name='филиал')
    service             = models.ForeignKey(Service, verbose_name='услуга')
    datetime            = models.DateTimeField(verbose_name='дата/время заказа')
    executors_required  = models.IntegerField(default=0, verbose_name='исполнителей требуется')
    start_place         = models.CharField(max_length=128, verbose_name='место начала')
    finish_place        = models.CharField(max_length=128, blank=True, verbose_name='место окончания')
    description         = models.TextField(max_length=256, blank=True, verbose_name='описание')
    cargo               = models.CharField(max_length=64, verbose_name='груз')
    payment_method      = models.ForeignKey(PaymentMethod, verbose_name='способ оплаты')