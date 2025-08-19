from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<int:user_id>/<str:token>/', views.activate_user, name='activate-user'),
    path('redirect-dashboard/', views.redirect_dashboard, name='redirect-dashboard'),
    path('assign-role/<int:user_id>/', views.assign_role, name='assign-role'),
    
    # 👇 Add this line
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin/create-group/',views.create_group,name='create-group'),
    path('admin/group-list/',views.group_list,name='group-list')
    
]
