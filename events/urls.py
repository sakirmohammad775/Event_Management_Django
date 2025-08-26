from django.urls import path
from . import views

urlpatterns = [
    # dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin-dashboard'),
    path('dashboard/organizer/', views.organizer_dashboard, name='organizer-dashboard'),
    path('dashboard/participant/', views.participant_dashboard, name='participant-dashboard'),

    # events
    path('', views.event_list, name='event-list'),
    path('event/<int:event_id>/', views.event_detail, name='event-detail'),
    path('event/create/', views.event_create, name='event-create'),
    path('event/<int:event_id>/update/', views.event_update, name='event-update'),
    path('event/<int:event_id>/delete/', views.event_delete, name='event-delete'),
    path('event/<int:event_id>/rsvp/', views.event_rsvp, name='event-rsvp'),

    # categories
    path('categories/', views.category_list, name='category-list'),
    path('categories/create/', views.category_create, name='category-create'),
    path('categories/<int:category_id>/update/', views.category_update, name='category-update'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category-delete'),
]
