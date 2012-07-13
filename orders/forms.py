# -*- coding: utf-8 -*-
from django import forms
from orders.models import Order, Work
from persons.models import Customer, Broker
import re
from datetime import datetime
from prices.models import Branch, Service, PaymentMethod
class OrderForm(forms.ModelForm):
    autofill_fields = ('code', 'customer', 'datetime', 'executors_required',\
                       'start', 'contacts', 'finish', 'cargo', 'description',\
                       'broker', 'branch', 'service', 'payment_method',)
    cut_sms = forms.CharField(label=u'Сокращенное SMS', required=False, widget=forms.Textarea(attrs={'disabled': True}))
    class Meta:
        model = Order
    
    def autofill_on_sms(self):
        for field in self.autofill_fields:
            getattr(self, 'autofill_' + field)()
            
    def autofill_code(self):
        if not self.data['code'] or self.data['code'] == '0':
            founds = re.findall(u'^Заказ #(\d+)', self.data['sms'])
            if len(founds) > 0:
                self.data['code'] = founds[0]
    
    def autofill_customer(self):
        if not self.data['customer']:
            founds = re.findall(u'Заказчик: (.+?);', self.data['sms'])
            if len(founds) > 0:
                try:
                    import_name_prefix = founds[0].split()[0]
                    self.data['customer'] = Customer.objects.get(name__istartswith=import_name_prefix).pk
                except:
                    pass
    def autofill_datetime(self):
        if not self.data['datetime_0'] or not self.data['datetime_1']:
            founds = re.findall(u'(\d\d/\d\d/\d\d \d\d:\d\d)', self.data['sms'])
            if len(founds) > 0:
                try:
                    self.data['datetime_0'] = datetime.strptime(founds[0], '%d/%m/%y %H:%M').date()
                    self.data['datetime_1'] = datetime.strptime(founds[0], '%d/%m/%y %H:%M').time()
                except:
                    pass
                
    def autofill_executors_required(self):
        if not self.data['executors_required'] or self.data['executors_required'] == '0':
            founds = re.findall(u'Старт: (\d+?)', self.data['sms'])
            if len(founds) > 0:
                try:
                    self.data['executors_required'] = founds[0]
                except:
                    pass
    
    def autofill_start(self):
        if not self.data['start']:
            founds = re.findall(u'Старт: \d+ .+?\s(.+?);', self.data['sms'])
            if len(founds) > 0:
                try:
                    self.data['start'] = founds[0]
                except:
                    pass
    def autofill_contacts(self):
        if not self.data['contacts']:
            founds = re.findall(u'СтЛица: (.+?);', self.data['sms'])
            if len(founds) > 0:
                try:
                    self.data['contacts'] = founds[0]
                except:
                    pass
                
    def autofill_finish(self):
        if not self.data['finish']:
            founds = re.findall(u'Финиш: (.+?);', self.data['sms'])
            if len(founds) > 0:
                try:
                    self.data['finish'] = founds[0]
                except:
                    pass
                
    def autofill_cargo(self):
        if not self.data['cargo']:
            founds = re.findall(u'Груз: (.+?);', self.data['sms'])
            if len(founds) > 0:
                try:
                    self.data['cargo'] = founds[0]
                except:
                    pass
    def autofill_description(self):
        if not self.data['description']:
            founds = re.findall(u'Инфо: (.+?);', self.data['sms'])
            if len(founds) > 0:
                try:
                    self.data['description'] = founds[0]
                except:
                    pass
    
    def autofill_broker(self):
        if not self.data['broker']:
            try:
                self.data['broker'] = Broker.objects.get(id=2)
            except:
                pass

    def autofill_branch(self):
        if not self.data['branch']:
            try:
                branches = Branch.objects.values_list('name', 'id')
                rating = []
                max_len = len(self.data['sms'])
                lower = self.data['sms'].lower()
                for branch in branches:
                    position = lower.find(branch[0].lower())
                    rating.append((position if position != -1 else max_len, branch[1]))
                self.data['branch'] = sorted(rating)[0][1]
            except:
                pass            
    def autofill_service(self):
        if not self.data['service']:
            try:
                self.data['service'] = Service.objects.get(name=u'Грузчики СамЭкспресс').pk
            except:
                pass
    def autofill_payment_method(self):
        if not self.data['payment_method']:
            founds = re.findall(u'Оплата: (.+)$', self.data['sms'])
            if len(founds) > 0:
                try:
                    import_method_prefix = founds[0].split()[0]
                    self.data['payment_method'] = PaymentMethod.objects.get(name__iexact=import_method_prefix).pk
                except:
                    pass

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('instance') and kwargs['instance'] is not None:
            if not kwargs.has_key('initial'):
                kwargs['initial'] = {}
            kwargs['initial']['cut_sms'] = kwargs['instance'].cut_sms()
        super(OrderForm, self).__init__(*args, **kwargs)
        if not kwargs.has_key('instance') and self.data.has_key('sms') and len(self.data['sms']) > 0:
            self.autofill_on_sms() 
        for elem in ('service', 'branch', 'payment_method'):
            self.fields[elem].widget.attrs['onMouseUp'] = 'allChanged()'
            self.fields[elem].widget.attrs['onKeyUp'] = 'allChanged()'
        self.fields['executors_required'].label = 'Требуется исполнителей'

class WorkForm(forms.models.ModelForm):
    model = Work
    def __init__(self, *args, **kwargs):
        super(WorkForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs['onKeyUp'] = 'quantityChanged(this.id)'
        self.fields['total'].widget.attrs['onKeyUp'] = 'totalChanged(this.id)'