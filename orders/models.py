# -*- coding: utf-8 -*-
from django.db import models
from prices.models import Branch, PaymentMethod, Service, ExecutorStatus
from django.db.models.base import Model
from persons.models import Executor
from django.db.models import F
from common.models import ViewManager

class Work(Model):
    '''
    Работа одного исполнителя
    '''
    class Meta:
        verbose_name = 'work'
        verbose_name_plural = 'works'
    def __unicode__(self):
        return u'work (order:%s; executor:%s)' % (self.order, self.executor)
    quantity         = models.FloatField(default=0.0, verbose_name='quality')
    executor         = models.ForeignKey('persons.Executor', related_name='test', verbose_name='executor')
    order            = models.ForeignKey('Order', verbose_name='order')
    accepted         = models.BooleanField(default=False, verbose_name='accepted')
    finished         = models.BooleanField(default=False, verbose_name='finished')
    executor_status  = models.ForeignKey(ExecutorStatus, verbose_name='Executorstatus')
    fee_through      = models.ForeignKey('persons.Person', null=True, blank=True, verbose_name='Order Fee')
    total            = models.FloatField(default=0.0, verbose_name='Total')
    broker_sum       = models.FloatField(default=0.0, verbose_name='Broker Sum')
    executor_sum     = models.FloatField(default=0.0, verbose_name='Executor Sum')
    executor_balance = models.FloatField(default=0.0, verbose_name='Executor Balance')
    customer_balance = models.FloatField(default=0.0, verbose_name='Customer Balance')
    broker_balance   = models.FloatField(default=0.0, verbose_name='Broker Balance')
    

class BaseOrder(Model):
    class Meta:
        verbose_name = 'order'
        verbose_name_plural = 'orders'
        abstract = True
    def __unicode__(self):
        return ' '.join((unicode(self.customer), unicode(self.datetime.strftime('%d.%m.%Y %H:%M'))))
    dispatcher          = models.ForeignKey('persons.Dispatcher', verbose_name='Dispatcher')
    broker              = models.ForeignKey('persons.Broker', null=True, blank=True, verbose_name='Broker')
    customer            = models.ForeignKey('persons.Customer', verbose_name='Customer')
    code                = models.IntegerField(default=0, verbose_name='Code')
    branch              = models.ForeignKey(Branch, verbose_name='Branch')
    service             = models.ForeignKey(Service, verbose_name='Service')
    datetime            = models.DateTimeField(verbose_name='Order Date')
    executors_required  = models.IntegerField(default=0, verbose_name='?')
    start               = models.CharField(max_length=128, verbose_name='Start')
    finish              = models.CharField(max_length=128, blank=True, verbose_name='Finish')
    contacts            = models.CharField(max_length=128, blank=True, verbose_name='Contacts')
    description         = models.TextField(max_length=256, blank=True, verbose_name='Description')
    cargo               = models.CharField(max_length=64, verbose_name='Cargo')
    payment_method      = models.ForeignKey(PaymentMethod, verbose_name='Payment Method')
    sms                 = models.TextField(max_length=1024, verbose_name='SMS', null=True, blank=True)
    def cut_sms(self):
        return u'Customer: %s; %s; %s Datetime: %s; %s; Cargo: %s%s; Description: %s' \
            % (self.customer, self.datetime.strftime('%d/%m/%y %H:%M'), self.executors_required, self.start, self.contacts, self.cargo,\
               u'; ' + self.description if len(self.description) > 0 else u'', self.payment_method)
    cut_sms.short_description = 'SMS'
    
class Order(BaseOrder):
    executors           = models.ManyToManyField(Executor, through='Work')

class ExtendedOrder(BaseOrder):
    class Meta(BaseOrder.Meta):
        db_table = 'orders_order_extended'
    base_model = Order
    objects = ViewManager()
    executors_accepted  = models.IntegerField(default=0, verbose_name='+')
    executors_set       = models.IntegerField(default=0, verbose_name='-')
    executors_verified  = models.IntegerField(default=0, verbose_name='=')
    quantity            = models.FloatField(default=0, verbose_name='Quantity')
    total               = models.FloatField(default=0, verbose_name='Total')
    executors           = models.CharField(max_length=1024, verbose_name='Executors')
    def save(self, force_insert=False, force_update=False, using=None):
        if force_insert and force_update:
            raise ValueError("Cannot force both insert and updating in model saving.")
        self.save_base(cls=self.base_model, using=using, force_insert=force_insert, force_update=force_update)
    def delete(self, using=None):
        return self.base_model.objects.get(pk=self.pk).delete()


class ExtendedPlanManager(models.Manager):
    def get_query_set(self):
        return super(ExtendedPlanManager, self).get_query_set().filter(executors_accepted__lt=F('executors_required'))
    
class ExtendedPlan(ExtendedOrder):
    class Meta:
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'
        proxy = True
    objects = ExtendedPlanManager()
    
class FinishedOrderManager(models.Manager):
    def get_query_set(self):
        return super(FinishedOrderManager, self).get_query_set().filter(executors_accepted=F('executors_required')).filter(executors_verified__lt=F('executors_required'))
    
class ExtendedFinishedOrder(ExtendedOrder):
    class Meta:
        verbose_name = 'Finishorder'
        verbose_name_plural = 'FinishOrders'
        proxy = True
    objects = FinishedOrderManager()
