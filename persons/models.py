# -*- coding: utf-8 -*-
from new import classobj
from django.db import models
from django.db.models import Q
from prices.models import Branch
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from common.models import ViewManager
import orders.models
from django.core import urlresolvers

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
    description     = models.TextField(max_length=1024, blank=True, null=True, verbose_name='подробное описание')

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
    executors_count        = models.IntegerField(verbose_name='И', blank=True, null=True)
    def save(self, force_insert=False, force_update=False, using=None):
        if force_insert and force_update:
            raise ValueError("Cannot force both insert and updating in model saving.")
        self.save_base(cls=self.base_model, using=using, force_insert=force_insert, force_update=force_update)
    def delete(self, using=None):
        return self.base_model.objects.get(pk=self.pk).delete()
    def previous_order(self):
        try:
            return orders.models.Work.objects.filter(executor_id=self.pk).filter(Q(finished=True) | Q(quantity__gt=0.0) | Q(order__datetime__lt=datetime.now().date())).order_by('-order__datetime')[0].order
        except IndexError:
            pass
    previous_order.short_description = u'предыдущий заказ'
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
    def content_object_url(self):
        replaceable_models = (orders.models.ExtendedOrder,)
        for model in replaceable_models:
            if self.content_object.__class__ == model.base_model:
                meta = model._meta
            else:
                meta = self.content_object._meta
        url = urlresolvers.reverse('admin:%s_%s_change' % (meta.app_label, meta.module_name), args=(self.content_object.pk,))
        return '<a href="%s">%s</a>' % (url, self.content_object) 
    content_object_url.allow_tags = True
    content_object_url.short_description = 'Объект'

class BranchExtendedExecutorManager(ViewManager):
    def __init__(self, branch_id):
        self.branch_id = branch_id
        super(BranchExtendedExecutorManager, self).__init__()
    def get_query_set(self):
        return super(BranchExtendedExecutorManager, self).get_query_set().filter(branch_id=self.branch_id, category__lt=4)
branch_executors = [classobj(str(branch.english_name) + 'ExtendedExecutor', (ExtendedExecutor,), {'objects': BranchExtendedExecutorManager(branch_id=branch.id), 'Meta': classobj('Meta', (ExtendedExecutor.Meta,), {'proxy': True, 'verbose_name_plural': u'исполнители - ' + branch.name})}) for branch in Branch.objects.all()]
