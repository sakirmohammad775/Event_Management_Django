from django.urls import path
from . import views

urlpatterns = [
    # Public
    path("", views.event_list, name="event-list"),
    path("events/<int:pk>/", views.event_detail, name="event-detail"),

    # Category (Admin only)
     # Categories
    path("categories/", views.category_list, name="category-list"),
    path("categories/add/", views.category_create, name="category-create"),
    path("categories/<int:pk>/edit/", views.category_update, name="category-update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category-delete"),

     # Events
    path("", views.event_list, name="event-list"),
    path("<int:pk>/", views.event_detail, name="event-detail"),
    path("add/", views.event_create, name="event-create"),
    path("<int:pk>/edit/", views.event_update, name="event-update"),
    path("<int:pk>/delete/", views.event_delete, name="event-delete"),

    # Dashboards
    
    path("dashboard/participant/", views.participant_dashboard, name="participant-dashboard"),
    path("dashboard/organizer/", views.organizer_dashboard, name="organizer-dashboard"),
]


    


