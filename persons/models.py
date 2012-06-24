from django.db import models
from prices.models import Branch
from datetime import datetime

class Person(models.Model):
    class Meta:
        verbose_name = '����'
        verbose_name_plural = '����'
        ordering = ('surname', 'name')
    def __unicode__(self):
        return u' '.join((self.surname, self.name))
    surname         = models.CharField(max_length=128, verbose_name='�������', blank=True)
    name            = models.CharField(max_length=128, verbose_name='���', blank=True)
    phone           = models.CharField(max_length=128, verbose_name='�������', blank=True)
    birthday        = models.DateField(verbose_name='���� ��������', null=True, blank=True)
    address         = models.TextField(max_length=256, verbose_name='�����', blank=True)
    total_debt      = models.FloatField(default=0.0, verbose_name='�������������', null=False)
    appearance_date = models.DateField(verbose_name='��������', null=True, blank=True, default=datetime.today)
    branch          = models.ForeignKey(Branch, verbose_name='������', null=True, blank=True)
