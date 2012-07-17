# -*- coding: utf-8 -*-
from django.db import models
from persons.models import Person
from datetime import date

class SettlementItem(models.Model):
    '''
    Статья доходов/расходов
    '''
    class Meta:
        verbose_name = 'статья'
        verbose_name_plural = 'статьи'
        ordering = ('code',)
        
    name = models.CharField(max_length=128, verbose_name=u'название')
    code = models.CharField(max_length=3, verbose_name=u'код')
    
    def __unicode__(self):
        return u' '.join((self.code, self.name))
class MoneyOperation(models.Model):
    class Meta:
        verbose_name = 'денежная операция'
        verbose_name_plural = 'денежные операции'
        abstract = True
        ordering = ('-date',)
    
    def __unicode__(self):
        return ' '.join((unicode(self._meta.verbose_name, 'utf8').capitalize(), u'лица', unicode(self.person), u'от', unicode(self.date)))
    person          = models.ForeignKey(Person, verbose_name='лицо')
    date            = models.DateField(verbose_name='дата расчета', default=date.today)
    total           = models.FloatField(verbose_name='сумма')
    settlement_item = models.ForeignKey(SettlementItem, default=1, blank=False, null=False, verbose_name='тип расчета')
    note            = models.CharField(max_length=256, blank=True, null=True, verbose_name='примечание')
    
class Income(MoneyOperation):
    '''
    Приход денег в кассу
    '''
    class Meta(MoneyOperation.Meta):
        verbose_name = 'приход'
        verbose_name_plural = 'приходы'

class Expense(MoneyOperation):
    '''
    Расход денег из кассы
    '''
    class Meta(MoneyOperation.Meta):
        verbose_name = 'расход'
        verbose_name_plural = 'расходы'
    
class MoneyTransfer(models.Model):
    '''
    Передача денег между лицами
    '''
    class Meta:
        verbose_name = 'передача'
        verbose_name_plural = 'передачи'
        ordering = ('-date',)
    
    def __unicode__(self):
        return ' '.join((u'Передача от лица', unicode(self.from_person), u'лицу', unicode(self.to_person)))
    
    from_person = models.ForeignKey(Person, verbose_name='отдал', related_name='giving_person_set')
    to_person = models.ForeignKey(Person, verbose_name='принял', related_name='getting_person_set')
    total = models.FloatField(default=0, verbose_name='сумма')
    date = models.DateField(verbose_name='дата', default=date.today())
    note = models.CharField(max_length=256, verbose_name='примечание', blank=True)