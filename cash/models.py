# -*- coding: utf-8 -*-
from django.db import models
from persons.models import Person
from datetime import date

class SettlementItem(models.Model):
    '''
    Статья доходов/расходов
    '''
    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        ordering = ('code',)
        
    name = models.CharField(max_length=128, verbose_name=u'Name')
    code = models.CharField(max_length=3, verbose_name=u'code')
    
    def __unicode__(self):
        return u' '.join((self.code, self.name))
class MoneyOperation(models.Model):
    class Meta:
        verbose_name = 'Money Operation'
        verbose_name_plural = 'Money Operations'
        abstract = True
        ordering = ('-date',)
    
    def __unicode__(self):
        return ' '.join((unicode(self._meta.verbose_name, 'utf8').capitalize(), u'person', unicode(self.person), u'date', unicode(self.date)))
    person          = models.ForeignKey(Person, verbose_name='Person')
    date            = models.DateField(verbose_name='Transit date', default=date.today)
    total           = models.FloatField(verbose_name='Total')
    settlement_item = models.ForeignKey(SettlementItem, default=1, blank=False, null=False, verbose_name='Settlement Item')
    note            = models.CharField(max_length=256, blank=True, null=True, verbose_name='note')
    
class Income(MoneyOperation):
    '''
    Приход денег в кассу
    '''
    class Meta(MoneyOperation.Meta):
        verbose_name = 'Income'
        verbose_name_plural = 'Incomes'

class Expense(MoneyOperation):
    '''
    Расход денег из кассы
    '''
    class Meta(MoneyOperation.Meta):
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
    
class MoneyTransfer(models.Model):
    '''
    Передача денег между лицами
    '''
    class Meta:
        verbose_name = 'Transfer'
        verbose_name_plural = 'MoneyTransfers'
        ordering = ('-date',)
    
    def __unicode__(self):
        return ' '.join((u'Money From', unicode(self.from_person), u'Money Receiver', unicode(self.to_person)))
    
    from_person = models.ForeignKey(Person, verbose_name='FromPerson', related_name='giving_person_set')
    to_person = models.ForeignKey(Person, verbose_name='ToPerson', related_name='getting_person_set')
    total = models.FloatField(default=0, verbose_name='Total')
    date = models.DateField(verbose_name='Date', default=date.today())
    note = models.CharField(max_length=256, verbose_name='notes', blank=True)
