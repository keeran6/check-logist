# -*- coding: utf-8 -*-
from django import forms
from django.db.models import F
from persons.models import Executor
from orders.models import Plan
class ExecutorForm(forms.ModelForm):
    
    class Meta:
        model = Executor
    
    current_order = forms.ModelChoiceField(queryset=Plan.objects.filter(executors_set__lt=F('executors_required')), label='Текущий заказ', required=False)
    
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('initial'):
            kwargs['initial'] = {} 
        if kwargs.has_key('instance') and kwargs['instance'] is not None:
            order = kwargs['instance'].current_order()
            if order is None:
                kwargs['initial']['current_order'] = None
                super(ExecutorForm, self).__init__(*args, **kwargs)
            else:
                super(ExecutorForm, self).__init__(*args, **kwargs)
                self.fields['current_order'].required = False
                self.fields['current_order'].choices = [(0, order)]
                self.fields['current_order'].widget.attrs['disabled'] = True
                
        
        
                
    def save(self, commit=True):
        pass
        #=======================================================================
        # instance = super(PersonForm, self).save(commit=commit)
        # if commit:
        #    cursor = connection.cursor()
        #    for entity in ('executor', 'customer', 'dispatcher', 'broker'):
        #        if self.cleaned_data['is_%s' % entity]:
        #            if not ContentType.objects.get(model=entity).model_class().objects.filter(person_ptr=instance).exists():
        #                cursor.execute('REPLACE INTO persons_%s (person_ptr_id) VALUES (%%s)' % entity, [instance.pk])
        #        else:
        #            cursor.execute('DELETE FROM persons_%s WHERE person_ptr_id = %%s' % entity, [instance.pk])
        # transaction.commit_unless_managed()
        # return instance
        #=======================================================================