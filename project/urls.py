"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from YAAS.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', start, name='index'),
    url(r'^yaas/$', start),
    url(r'^register/$', register),
    url(r'^login/$', signin),
    url(r'^signout/$', signout),
    url(r'^login_error/$', login_error),
    url(r'^edit_profile/$', edit_profile),
    url(r'^change_password/$', change_password),
    url(r'^create_auction/$', create_auction),
    url(r'^confirm_auction/$', confirm_auction),
    url(r'^show_auction/(?P<id>[0-9]+)', show_auction),
    url(r'^place_bid/(?P<id>[0-9]+)', place_bid),
    url(r'^edit_auction/(?P<id>[0-9]+)', edit_auction),
    url(r'^ban_auction/(?P<id>[0-9]+)', ban_auction),
    url(r'^edit/(?P<hash>\w{32})', edit),



]
