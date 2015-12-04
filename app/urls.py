__author__ = 'Ben'

from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    url(r'^data/$', csrf_exempt(views.data)),
    url(r'^setup_data/$', views.setup_data),
    url(r'^$', views.index),
]