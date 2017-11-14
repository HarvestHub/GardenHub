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


account_patterns = [
    url(r'^$', views.my_account),
    url(r'^settings/', views.account_settings),
    url(r'^delete/', views.delete_account),
]

urlpatterns = [
    url(r'^$', views.home),
    url(r'^login/$', views.login_user),
    url(r'^admin/', admin.site.urls),
    url(r'^account/$', views.my_account),
    # Orders
    url(r'^orders/$', views.orders),
    url(r'^orders/new/$', views.new_order),
    url(r'^order/(?P<orderId>.*)/$', views.view_order),
    # Plots
    url(r'^plots/$', views.plots),
    url(r'^plot/(?P<plotId>.*)/edit/$', views.edit_plot),
    # Gardens
    url(r'^gardens/$', views.gardens),
    url(r'^garden/(?P<gardenId>.*)/edit/$', views.edit_garden),
    # Default auth views https://docs.djangoproject.com/en/1.11/topics/auth/default/#using-the-views
    url('^', include('django.contrib.auth.urls')),
]
