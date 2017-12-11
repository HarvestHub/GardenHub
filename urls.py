"""gardenhub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
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
    url(r'^logout/$', views.logout_user),
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include(account_patterns)),
    url(r'^activate/(?P<uuid>[0-9a-z\-]+)/$', views.activate_account),
    # Orders
    url(r'^orders/$', views.orders),
    url(r'^orders/new/$', views.new_order),
    url(r'^order/(?P<orderId>[0-9]+)/$', views.view_order),
    # Plots
    url(r'^plots/$', views.plots),
    url(r'^plot/(?P<plotId>[0-9]+)/edit/$', views.edit_plot),
    # Gardens
    url(r'^gardens/$', views.gardens),
    url(r'^garden/(?P<gardenId>[0-9]+)/$', views.view_garden),
    url(r'^garden/(?P<gardenId>[0-9]+)/edit/$', views.edit_garden),
    # API
    url(r'^_api/crops/(?P<plotId>[0-9]+)/$', views.api_crops),
    # Default auth views https://docs.djangoproject.com/en/2.0/topics/auth/default/#using-the-views
    url('^', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
