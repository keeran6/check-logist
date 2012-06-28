# -*- coding: utf-8 -*-
from django.db import models

class Branch(models.Model):
    class Meta:
        verbose_name = 'филиал'
        verbose_name_plural = 'филиалы'
        ordering = ('name',)    
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=32, blank=False, null=False, verbose_name='название')
    
class PaymentMethod(models.Model):
    '''
    Вид оплаты
    '''
    class Meta:
        verbose_name = 'вид оплаты'
        verbose_name_plural = 'виды оплаты'
        ordering = ('name',)
    def __unicode__(self):
        return self.name
    name                = models.CharField(max_length=32, verbose_name=u'название')
    executor_multiplyer = models.FloatField()
    broker_multiplyer   = models.FloatField()
    customer_multiplyer = models.FloatField()
    
class Service(models.Model):
    '''
    Услуга, оказываемая клиентам
    '''
    class Meta:
        verbose_name = 'услуга'
        verbose_name_plural = 'услуги'
        ordering = ('name',)
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=128, verbose_name=u'название')
    
class Price(models.Model):
    class Meta:
        verbose_name = 'цена'
        verbose_name_plural = 'цены'    
        ordering = ('branch', 'service', 'payment_method')
    payment_method   = models.ForeignKey(PaymentMethod, verbose_name='способ оплаты')
    branch           = models.ForeignKey(Branch, verbose_name='филиал')
    service          = models.ForeignKey(Service, verbose_name='услуга')
    executor_percent = models.FloatField(default=0, verbose_name='% исполнителя')
    broker_percent   = models.FloatField(default=0, verbose_name='% посредника')
    cost             = models.FloatField(default=0, verbose_name='цена')