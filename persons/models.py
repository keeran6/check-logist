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

STATES = (
          (0, u''),
          (1, u'Свободен'),
          (2, u'Отключен'),
          (3, u'Не берет'),
          (4, u'Освободится')
          )

class Person(models.Model):
    class Meta:
        verbose_name = 'person'
        verbose_name_plural = 'persons'
        ordering = ('name',)
    def __unicode__(self):
        return self.name
    name            = models.CharField(max_length=128, verbose_name='Name', blank=False, null=False)
    phone           = models.CharField(max_length=128, verbose_name='Phone', blank=True)
    birthday        = models.DateField(verbose_name='Birthday', null=True, blank=True)
    address         = models.CharField(max_length=256, verbose_name='Address', blank=True)
    total_debt      = models.FloatField(default=0.0, verbose_name='Debt', null=False, blank=True)
    appearance_date = models.DateField(verbose_name='Appearance_date', null=True, blank=True, default=datetime.today)
    branch          = models.ForeignKey(Branch, verbose_name='Branch', null=True, blank=False)
    note            = models.CharField(max_length=128, verbose_name='notes', blank=True)
    description     = models.TextField(max_length=1024, blank=True, null=True, verbose_name='Description')

class Customer(Person):
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

class Broker(Person):
    class Meta:
        verbose_name = 'Broker'
        verbose_name_plural = 'Brokers'

class Dispatcher(Person):
    class Meta:
        verbose_name = 'Dispatcher'
        verbose_name_plural = 'Dispatchers'
        
class BaseExecutor(Person):
    class Meta:
        verbose_name = 'Executor'
        verbose_name_plural = 'Executors'
        abstract = True
        ordering = ('name',)
    free_datetime = models.DateField(verbose_name='FreeDate', default=datetime.now, blank=True, null=True)
    last_contact  = models.DateTimeField(verbose_name='Lastdate', auto_now=True)
    category = models.IntegerField(verbose_name='К', default=0, help_text='0 - новенький, 1 - регулярно работает, 2 - редко работает, 3 - почти не работает, 4 - не работает')
    state = models.IntegerField(verbose_name='State', choices=STATES, blank=True, default=0)
    def age(self):
        if self.birthday:
            return (datetime.now().date() - self.birthday).days / 365
    age.short_description = 'age'

class Executor(BaseExecutor):
    pass

class ExtendedExecutor(BaseExecutor):
    class Meta(BaseExecutor.Meta):
        db_table = 'persons_executor_extended'
    base_model = Executor
    objects = ViewManager()
    current_order          = models.ForeignKey('orders.Order', verbose_name='Current order', blank=True, null=True)
    current_order_accepted = models.NullBooleanField(verbose_name='+', blank=True, null=True)
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
    previous_order.short_description = u'previous order'
class Debt(models.Model):
    class Meta:
        verbose_name = 'Debt'
        verbose_name_plural = 'Debts'
    person = models.ForeignKey(Person, verbose_name='person')
    date = models.DateField(verbose_name='date')
    total = models.FloatField(verbose_name='Total')
    note = models.CharField(max_length=128, verbose_name='Notes')
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
    content_object_url.short_description = 'Content'

class BranchExtendedExecutorManager(ViewManager):
    def __init__(self, branch_id):
        self.branch_id = branch_id
        super(BranchExtendedExecutorManager, self).__init__()
    def get_query_set(self):
        return super(BranchExtendedExecutorManager, self).get_query_set().filter(branch_id=self.branch_id, category__lt=4, category__gt=0)
branch_executors = [classobj(str(branch.english_name) + 'ExtendedExecutor', (ExtendedExecutor,), {'objects': BranchExtendedExecutorManager(branch_id=branch.id), 'Meta': classobj('Meta', (ExtendedExecutor.Meta,), {'proxy': True, 'verbose_name_plural': u'исполнители - ' + branch.name})}) for branch in Branch.objects.all()]
class BranchPotentialExtendedExecutorManager(ViewManager):
    def __init__(self, branch_id):
        self.branch_id = branch_id
        super(BranchPotentialExtendedExecutorManager, self).__init__()
    def get_query_set(self):
        return super(BranchPotentialExtendedExecutorManager, self).get_query_set().filter(branch_id=self.branch_id, category__lt=1)
branch_potential_executors = [classobj(str(branch.english_name) + 'PotentialExtendedExecutor', (ExtendedExecutor,), {'objects': BranchPotentialExtendedExecutorManager(branch_id=branch.id), 'Meta': classobj('Meta', (ExtendedExecutor.Meta,), {'proxy': True, 'verbose_name_plural': u'потенциальные - ' + branch.name})}) for branch in Branch.objects.all()]
