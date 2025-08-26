from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Event, Category, RSVP
from .forms import EventForm, CategoryForm
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date
from users.decorators import group_required
from django.contrib.auth.models import User


def home(request):
    return render(request, 'home.html')
# Event List (with select_related + prefetch_related)

######## Dashboard View #####

def organizer_dashboard(request):
    today = timezone.now().date()
    user = request.user  # Organizer

    # ✅ Filter only events created by this organizer
    events = Event.objects.filter(organizer=user).select_related('category')

    total_events = events.count()
    total_participants = RSVP.objects.filter(event__in=events).count()
    upcoming_events = events.filter(date__gt=today).count()
    past_events = events.filter(date__lt=today).count()
    todays_events = events.filter(date=today)

    context = {
        'total_events': total_events,
        'total_participants': total_participants,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'todays_events': todays_events,
        'events': events,
    }
    return render(request, 'dashboard/organizer_dashboard.html', context)


def participant_dashboard(request):
    user = request.user
    upcoming_rsvps = Event.objects.filter(rsvp__user=user, date__gte=timezone.now())
    past_rsvps = Event.objects.filter(rsvp__user=user, date__lt=timezone.now())

    context = {
        'upcoming_rsvps': upcoming_rsvps,
        'past_rsvps': past_rsvps,
    }
    return render(request, 'dashboard/participant_dashboard.html', context)


def admin_dashboard(request):
    total_events = Event.objects.count()
    total_participants = RSVP.objects.count()
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
    past_events = Event.objects.filter(date__lt=timezone.now()).count()
    users = User.objects.select_related().prefetch_related('groups').all()

    context = {
        "total_events": total_events,
        "total_participants": total_participants,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
        "users": users,  # For user management table
    }
    return render(request, "dashboard/admin_dashboard.html", context)



#### Event Views


def event_list(request):
    events = Event.objects.select_related('category').prefetch_related('participants')

    # Search
    search = request.GET.get('search')
    if search:
        events = events.filter(Q(name__icontains=search) | Q(location__icontains=search))

    # Category Filter
    category_id = request.GET.get('category')
    if category_id:
        events = events.filter(category_id=category_id)

    # Date Range Filter
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    if start_date and end_date:
        events = events.filter(date__range=[start_date, end_date])

    categories = Category.objects.all()
    return render(request, 'event_list.html', {
        'events': events,
        'categories': categories
    })

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    participants = event.rsvp_set.all()
    return render(request, 'event_detail.html', {'event': event, 'participants': participants})

def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, "Event created successfully!")
            return redirect('event-detail', event.id)
    else:
        form = EventForm()
    return render(request, 'event_form.html', {'form': form, 'title': 'Create Event'})

def event_update(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    form = EventForm(request.POST or None, request.FILES or None, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, "Event updated successfully!")
        return redirect('event-detail', event.id)
    return render(request, 'event_form.html', {'form': form, 'title': 'Update Event'})


def event_delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.success(request, "Event deleted successfully!")
    return redirect('event-list')

def event_rsvp(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if RSVP.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, "You already RSVP'd to this event.")
    else:
        RSVP.objects.create(user=request.user, event=event)
        messages.success(request, "RSVP successful! Confirmation sent.")
    return redirect('event-detail', event_id=event.id)


def event_search(request):
    query = request.GET.get('q', '')
    results = Event.objects.filter(
        name__icontains=query
    ) | Event.objects.filter(
        location__icontains=query
    )
    context = {
        'query': query,
        'results': results
    }
    return render(request, 'event_search.html', context)


def filter_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    events = Event.objects.filter(category=category).order_by("date", "time")
    return render(request, "category_form.html", {
        "category": category,
        "events": events
    })