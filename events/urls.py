from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/participant/', views.participant_dashboard, name='participant-dashboard'),
    path('dashboard/organizer/', views.organizer_dashboard, name='organizer-dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin-dashboard'),
    path('event/<int:event_id>/', views.event_detail, name='event-detail'),
    path('create/', views.event_create, name='event-create'),
    path('event/<int:event_id>/update/', views.event_update, name='event-update'),
    path('event/<int:event_id>/delete/', views.event_delete, name='event-delete'),
    path('event/<int:event_id>/rsvp/', views.event_rsvp, name='event-rsvp'),
    path('search/', views.event_search, name='event-search'),
    path('category/<int:category_id>/', views.filter_by_category, name='filter-category'),
]
