from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('no-permission/', views.no_permission, name='no-permission'),
]
