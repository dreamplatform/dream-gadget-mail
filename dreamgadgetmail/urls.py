
from django.conf.urls.defaults import *

urlpatterns = patterns('dreamgadgetmail.views',
    url(r'^mail_status/?$', 'mail_status', name='mail_status'),
)