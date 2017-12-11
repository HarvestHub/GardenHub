"""gardenhub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import path
from django.conf.urls import include
from django.conf.urls.static import static
from gardenhub import views
from django.contrib import admin


account_patterns = [
    path('', views.my_account),
    path('settings/', views.account_settings),
    path('delete/', views.delete_account),
]

urlpatterns = [
    path('', views.home),
    path('login/', views.login_user),
    path('logout/', views.logout_user),
    path('admin/', admin.site.urls),
    path('account/', include(account_patterns)),
    path('activate/<uuid:uuid>/', views.activate_account),
    # Orders
    path('orders/', views.orders),
    path('orders/new/', views.new_order),
    path('order/<int:orderId>/', views.view_order),
    # Plots
    path('plots/', views.plots),
    path('plot/<int:plotId>/edit/', views.edit_plot),
    # Gardens
    path('gardens/', views.gardens),
    path('garden/<int:gardenId>/', views.view_garden),
    path('garden/<int:gardenId>/edit/', views.edit_garden),
    # API
    path('_api/crops/<int:plotId>/', views.api_crops),
    # Default auth views https://docs.djangoproject.com/en/2.0/topics/auth/default/#using-the-views
    path('', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
