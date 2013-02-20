# -*- coding: utf-8 -*-
from django.db import models

class Branch(models.Model):
    class Meta:
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
        ordering = ('name',)
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=32, blank=False, null=False, verbose_name='name')
    english_name = models.CharField(max_length=32, blank=False, null=False, verbose_name='English_name')
    
class PaymentMethod(models.Model):
    '''
    Вид оплаты
    '''
    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payments Method'
        ordering = ('name',)
    def __unicode__(self):
        return self.name
    name                = models.CharField(max_length=32, verbose_name=u'name')
    executor_multiplyer = models.FloatField()
    broker_multiplyer   = models.FloatField()
    customer_multiplyer = models.FloatField()
    
class Service(models.Model):
    '''
    Услуга, оказываемая клиентам
    '''
    class Meta:
        verbose_name = 'service'
        verbose_name_plural = 'services'
        ordering = ('name',)
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=128, verbose_name=u'name')
    
class ExecutorStatus(models.Model):
    class Meta:
        verbose_name = 'status'
        verbose_name_plural = 'Status'
        ordering = ('name',)
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=32, verbose_name='name')
        
class Price(models.Model):
    class Meta:
        verbose_name = 'price'
        verbose_name_plural = 'prices'    
        ordering = ('branch', 'service', 'payment_method')
    payment_method   = models.ForeignKey(PaymentMethod, verbose_name='Payment Method')
    branch           = models.ForeignKey(Branch, verbose_name='Branch')
    service          = models.ForeignKey(Service, verbose_name='Service')
    executor_status  = models.ForeignKey(ExecutorStatus, verbose_name='Status')
    executor_percent = models.FloatField(default=0, verbose_name='% ExecutorPercentage')
    broker_percent   = models.FloatField(default=0, verbose_name='% BrokerPercentage')
    cost             = models.FloatField(default=0, verbose_name='cost')
