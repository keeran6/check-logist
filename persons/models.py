# -*- coding: utf-8 -*-
from new import classobj
from django.db import models
from prices.models import Branch
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from common.models import ViewManager
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
    def age(self):
        if self.birthday:
            return (datetime.now().date() - self.birthday).days / 365
    age.short_description = 'возраст'

class Executor(BaseExecutor):
    pass

class ExtendedExecutor(BaseExecutor):
    class Meta(BaseExecutor.Meta):
        db_table = 'persons_executor_extended'
    base_model = Executor
    objects = ViewManager()
    current_order          = models.ForeignKey('orders.Order', verbose_name='текущий заказ', blank=True, null=True)
    current_order_accepted = models.NullBooleanField(verbose_name='принят', blank=True, null=True)    
    def save(self, force_insert=False, force_update=False, using=None):
        if force_insert and force_update:
            raise ValueError("Cannot force both insert and updating in model saving.")
        self.save_base(cls=self.base_model, using=using, force_insert=force_insert, force_update=force_update)
    def delete(self, using=None):
        return self.base_model.objects.get(pk=self.pk).delete()
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

class BranchExtendedExecutorManager(ViewManager):
    def __init__(self, branch_id):
        self.branch_id = branch_id
        super(BranchExtendedExecutorManager, self).__init__()
    def get_query_set(self):
        return super(BranchExtendedExecutorManager, self).get_query_set().filter(branch_id=self.branch_id, category__lt=4)
branch_executors = [classobj(str(branch.english_name) + 'ExtendedExecutor', (ExtendedExecutor,), {'objects': BranchExtendedExecutorManager(branch_id=branch.id), 'Meta': classobj('Meta', (ExtendedExecutor.Meta,), {'proxy': True, 'verbose_name_plural': u'исполнители - ' + branch.name})}) for branch in Branch.objects.all()]
