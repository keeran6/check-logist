# -*- coding: utf-8 -*-
'''
Created on 21.07.2012

@author: Admin
'''
from django.db import models
class ViewQueryset(models.query.QuerySet):
    def delete(self):
        for obj in self:
            self.model.base_model.objects.get(pk=obj.pk).delete()
class ViewManager(models.Manager):
    def get_query_set(self):
        return ViewQueryset(self.model, using=self._db)
