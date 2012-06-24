from django.db import models

class Branch(models.Model):
    class Meta:
        verbose_name = 'филиал'
        verbose_name_plural = 'филиалы'
        ordering = ('name',)    
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=32, blank=False, null=False, verbose_name='название')
