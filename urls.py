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


urlpatterns = [
    url(r'^$', views.login),
    url(r'^admin/', admin.site.urls),
    url(r'^home/', views.home),
    url(r'^employee_views/ep_garden_assignments/', views.ep_garden_assignments),
    url(r'^employee_views/ep_garden_map/', views.ep_garden_map),
    url(r'^employee_views/ep_garden_assignments/', views.ep_garden_assignments),
    url(r'^gardener_views/edit_plot/', views.edit_plot),
    url(r'^gardener_views/my_gardens/', views.my_gardens),
    url(r'^gardener_views/schedule/', views.schedule),
    url(r'^manager_views/manage_garden/', views.manage_garden),
    url(r'^manager_views/manage_gardens_select/', views.manage_gardens_select),
    url(r'^manager_views/my_gardens/', views.my_gardens),
    url(r'^manager_views/view_gardens/', views.view_gardeners),
]
