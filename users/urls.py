# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<int:user_id>/<str:token>/', views.activate_user, name='activate'),

    # existing redirect (keep for compatibility)
    path('redirect-dashboard/', views.redirect_dashboard, name='redirect-dashboard'),

    # <-- ADD THIS so reverse('dashboard') works anywhere in the project -->
    path('dashboard/', views.redirect_dashboard, name='dashboard'),

    # admin views (actual admin page is in users.views.admin_dashboard)
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/assign-role/<int:user_id>/', views.assign_role, name='assign-role'),
    path('admin/create-group/', views.create_group, name='create-group'),
    path('admin/groups/', views.group_list, name='group-list'),
    path('admin/users/', views.user_list, name='user-list'),

    # (optionally) categories listing via users admin area (if you prefer)
    # path('admin/categories/', views.category_list, name='category-list'),
]
