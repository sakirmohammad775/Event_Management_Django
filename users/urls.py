from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect-dashboard/', views.redirect_dashboard, name='redirect-dashboard'),
    path('assign-role/<int:user_id>/', views.assign_role, name='assign-role'),
]
