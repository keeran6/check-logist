# -*- coding: utf-8 -*-
from django.db import models
from prices.models import Branch, PaymentMethod, Service
from django.db.models.base import Model
from persons.models import Executor
from django.db.models import F

class Work(Model):
    '''
    Работа одного исполнителя
    '''
    class Meta:
        verbose_name = 'работа'
        verbose_name_plural = 'работы'
    def __unicode__(self):
        return u'Работа (Заказ:%s; Исполнитель:%s)' % (self.order, self.executor)
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
        return ' '.join((unicode(self.customer), unicode(self.datetime.strftime('%d.%m.%Y %H:%M'))))
    dispatcher          = models.ForeignKey('persons.Dispatcher', verbose_name='диспетчер')
    broker              = models.ForeignKey('persons.Broker', null=True, blank=True, verbose_name='посредник')
    customer            = models.ForeignKey('persons.Customer', verbose_name='заказчик')
    code                = models.IntegerField(default=0, verbose_name='код')
    branch              = models.ForeignKey(Branch, verbose_name='филиал')
    service             = models.ForeignKey(Service, verbose_name='услуга')
    datetime            = models.DateTimeField(verbose_name='дата/время заказа')
    executors_required  = models.IntegerField(default=0, verbose_name='требуется')
    start               = models.CharField(max_length=128, verbose_name='место начала')
    finish              = models.CharField(max_length=128, blank=True, verbose_name='место окончания')
    contacts            = models.CharField(max_length=128, blank=True, verbose_name='контакты')
    description         = models.TextField(max_length=256, blank=True, verbose_name='описание')
    cargo               = models.CharField(max_length=64, verbose_name='груз')
    payment_method      = models.ForeignKey(PaymentMethod, verbose_name='способ оплаты')
    sms                 = models.TextField(max_length=1024, verbose_name='SMS', null=True, blank=True)
    def cut_sms(self):
        return u'Заказчик: %s; %s; %s человек %s; %s; Груз: %s%s; Оплата: %s' \
            % (self.customer, self.datetime.strftime('%d/%m/%y %H:%M'), self.executors_required, self.start, self.contacts, self.cargo,\
               u'; ' + self.description if len(self.description) > 0 else u'', self.payment_method)
    cut_sms.short_description = 'сокращенное смс'
    
class Order(BaseOrder):
    executors           = models.ManyToManyField(Executor, through='Work')

class ExtendedOrder(BaseOrder):
    class Meta(BaseOrder.Meta):
        db_table = 'orders_order_extended'
    executors_accepted  = models.IntegerField(default=0, verbose_name='приняли')
    executors_set       = models.IntegerField(default=0, verbose_name='отправлено')
    executors_verified       = models.IntegerField(default=0, verbose_name='выверено')
        

class ExtendedPlanManager(models.Manager):
    def get_query_set(self):
        return super(ExtendedPlanManager, self).get_query_set().filter(executors_accepted__lt=F('executors_required'))
    
class ExtendedPlan(ExtendedOrder):
    class Meta:
        verbose_name = 'план'
        verbose_name_plural = 'планы'
        proxy = True
    objects = ExtendedPlanManager()
    
class FinishedOrderManager(models.Manager):
    def get_query_set(self):
        return super(FinishedOrderManager, self).get_query_set().filter(executors_accepted=F('executors_required')).filter(executors_verified__lt=F('executors_required'))
    
class ExtendedFinishedOrder(ExtendedOrder):
    class Meta:
        verbose_name = 'выверка'
        verbose_name_plural = 'выверка'
        proxy = True
    objects = FinishedOrderManager()