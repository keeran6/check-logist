# -*- coding: utf-8 -*-
from django import forms
from django.db.models import F
from persons.models import Executor
from orders.models import ExtendedPlan, Order, Work
from prices.models import ExecutorStatus
import re

class ExecutorForm(forms.ModelForm):
    
    class Meta:
        model = Executor
    current_order = forms.ModelChoiceField(queryset=ExtendedPlan.objects.filter(executors_set__lt=F('executors_required')), required=False, label='Текущий заказ')
    executors_count = forms.IntegerField(required=False, label='Исполнителей на текущем заказе')
    
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('initial'):
            kwargs['initial'] = {} 
        if kwargs.has_key('instance') and kwargs['instance'] is not None:
            order = kwargs['instance'].current_order
            if order is None:
                kwargs['initial']['current_order'] = None
                kwargs['initial']['executors_count'] = 1
                super(ExecutorForm, self).__init__(*args, **kwargs)
            else:
                super(ExecutorForm, self).__init__(*args, **kwargs)
                self.fields['current_order'].choices = [(0, order)]
                self.fields['current_order'].widget.attrs['disabled'] = True
                self.fields['executors_count'].initial = Work.objects.filter(order_id=order.pk, executor_id=kwargs['instance'].pk).count()
                self.fields['executors_count'].widget.attrs['disabled'] = True
        else:
            super(ExecutorForm, self).__init__(*args, **kwargs)
            self.fields['current_order'].widget.attrs['disabled'] = True
            self.fields['executors_count'].widget.attrs['disabled'] = True
        
        
    def clean_current_order(self):
        if self.cleaned_data['current_order']:
            return Order.objects.get(pk=self.cleaned_data['current_order'].pk)
    def clean_phone(self):
        pat = re.compile('(?:8|\+7)(\d{3})(\d{3})(\d{2})(\d{2})')
        return pat.sub(r'8-\1-\2-\3-\4', self.cleaned_data['phone'])
    def save(self, commit=True):
        instance = super(ExecutorForm, self).save(commit=commit)
        if instance.pk and self.cleaned_data['current_order']:
            instance.state = 0
            for _ in xrange(self.cleaned_data['executors_count']):
                work = Work(order=self.cleaned_data['current_order'], executor_id=instance.pk, executor_status=ExecutorStatus.objects.get(name=u'Найм'))
                work.fee_through = None
                work.save()
        instance.save()
        return instance