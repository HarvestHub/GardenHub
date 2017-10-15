"""gardenhub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url, include
from gardenhub import views
from django.contrib import admin

settings_patterns = [
    url(r'^$', views.my_account),
    url(r'^settings/', views.account_settings),
    url(r'^delete/', views.delete_account),
]

harvest_patterns = [
    url(r'^$', views.harvest),
    url(r'^schedule/', views.schedule_harvest),
    url(r'^upcoming/', views.upcoming_harvests),
    url(r'^assignments/', views.harvest_assignments),
    url(r'^record/', views.record_harvest),
]

manage_patterns = [
    url(r'^$', views.manage),
    url(r'^gardens/(?P<gardenId>.*)', views.manage_garden),
    url(r'^gardens/(?P<gardenId>.*)/gardeners', views.manage_garden_gardeners),
    url(r'^gardens/(?P<gardenId>.*)/gardeners/edit', views.manage_garden_gardeners_edit),
    url(r'^gardens/(?P<gardenId>.*)/harvests', views.manage_garden_harvests),
    url(r'^gardens/(?P<gardenId>.*)/settings', views.manage_garden_settings),
]

urlpatterns = [
    url(r'^$', views.login),
    url(r'^admin/', admin.site.urls),
    url(r'^home/', views.home),
    url(r'^account/', include(settings_patterns)),
    url(r'^edit_plot/', views.edit_plot),
    url(r'^my_plots/', views.my_plots),
    url(r'^harvest/', include(harvest_patterns)),
    url(r'^manage/', include(manage_patterns)),
]
