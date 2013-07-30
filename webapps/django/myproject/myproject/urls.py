from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic.list_detail import object_list
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^accounts/', include('registration.urls')),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^', include('politics.urls')),
	
    # Examples:
    # url(r'^$', 'myproject.views.home', name='home'),
    # url(r'^myproject/', include('myproject.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	
)
