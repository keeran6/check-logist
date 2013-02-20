#from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from django.contrib import admin
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'hephaestus.views.home', name='home'),
    # url(r'^hephaestus/', include('hephaestus.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^', include(admin.site.urls)),
)
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 
urlpatterns += staticfiles_urlpatterns()
