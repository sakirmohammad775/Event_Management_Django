# events/views.py
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import EventForm, CategoryForm
from .models import Category, Event, RSVP


# -----------------------------
# Role helpers (keep it simple)
# -----------------------------
def is_admin(user):
    # superusers count as Admin
    return user.is_superuser or user.groups.filter(name="Admin").exists()


def is_organizer(user):
    return user.groups.filter(name="Organizer").exists()


def is_participant(user):
    return user.groups.filter(name="Participant").exists()


def is_admin_or_organizer(user):
    return is_admin(user) or is_organizer(user)


# -----------------------------------------
# One entry point: redirect by role
# -----------------------------------------
@login_required
def dashboard(request):
    if is_admin(request.user):
        return redirect("admin-dashboard")
    if is_organizer(request.user):
        return redirect("organizer-dashboard")
    # default = participant
    return redirect("participant-dashboard")


# -----------------------------------------
# Admin dashboard
# -----------------------------------------
@login_required
@user_passes_test(is_admin, login_url="no-permission")
def admin_dashboard(request):
    # global stats
    total_events = Event.objects.count()
    total_participants = RSVP.objects.count()
    upcoming_events = Event.objects.filter(date__gte=timezone.localdate()).count()
    past_events = Event.objects.filter(date__lt=timezone.localdate()).count()

    # event list with useful info
    events = (
        Event.objects.select_related("category", "organizer")
        .annotate(rsvp_count=Count("rsvp"))
        .order_by("-date", "-time")
    )

    context = {
        "total_events": total_events,
        "total_participants": total_participants,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
        "events": events,
    }
    return render(request, "dashboard/admin_dashboard.html", context)


# -----------------------------------------
# Organizer dashboard (only own events)
# -----------------------------------------
@login_required
@user_passes_test(is_organizer, login_url="no-permission")
def organizer_dashboard(request):
    user = request.user
    today = timezone.localdate()

    events_qs = (
        Event.objects.filter(organizer=user)
        .select_related("category")
        .annotate(rsvp_count=Count("rsvp"))
        .order_by("-date", "-time")
    )

    context = {
        "total_events": events_qs.count(),
        "total_participants": RSVP.objects.filter(event__in=events_qs.values("id")).count(),
        "upcoming_events": events_qs.filter(date__gt=today).count(),
        "past_events": events_qs.filter(date__lt=today).count(),
        "todays_events": events_qs.filter(date=today),
        "events": events_qs,
    }
    return render(request, "dashboard/organizer_dashboard.html", context)


# -----------------------------------------
# Participant dashboard (RSVPs)
# -----------------------------------------
@login_required
@user_passes_test(is_participant, login_url="no-permission")
def participant_dashboard(request):
    user = request.user
    today = timezone.localdate()

    upcoming_rsvps = (
        Event.objects.select_related("category", "organizer")
        .filter(rsvp__user=user, date__gte=today)
        .order_by("date", "time")
        .annotate(rsvp_count=Count("rsvp"))
    )
    past_rsvps = (
        Event.objects.select_related("category", "organizer")
        .filter(rsvp__user=user, date__lt=today)
        .order_by("-date", "-time")
        .annotate(rsvp_count=Count("rsvp"))
    )

    context = {"upcoming_rsvps": upcoming_rsvps, "past_rsvps": past_rsvps}
    return render(request, "dashboard/participant_dashboard.html", context)


# ======================================================
# Event CRUD + list/search/filter + RSVP
# ======================================================

def event_list(request):
    """
    Public listing page. Optimized and supports search + filters.
    """
    events = (
        Event.objects.select_related("category", "organizer")
        .annotate(rsvp_count=Count("rsvp"))
        .order_by("date", "time")
    )

    # search: name/location
    q = request.GET.get("q")
    if q:
        events = events.filter(Q(name__icontains=q) | Q(location__icontains=q))

    # filter by category
    category_id = request.GET.get("category")
    if category_id:
        events = events.filter(category_id=category_id)

    # date range
    start = request.GET.get("start")
    end = request.GET.get("end")
    if start and end:
        events = events.filter(date__range=[start, end])

    categories = Category.objects.all().order_by("name")
    return render(request, "event_list.html", {"events": events, "categories": categories})


def event_detail(request, event_id):
    event = get_object_or_404(
        Event.objects.select_related("category", "organizer").annotate(rsvp_count=Count("rsvp")),
        id=event_id,
    )
    participants = (
        RSVP.objects.select_related("user").filter(event=event).order_by("created_at")
        if hasattr(RSVP, "created_at")
        else RSVP.objects.select_related("user").filter(event=event)
    )
    return render(request, "event_detail.html", {"event": event, "participants": participants})


@login_required
@user_passes_test(is_admin_or_organizer, login_url="no-permission")
def event_create(request):
    """
    Admin & Organizer can create events.
    Organizer becomes the event.organizer automatically.
    """
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            # if your EventForm includes organizer, prefer the posted value for admins
            if not is_admin(request.user):
                event.organizer = request.user  # lock organizer to current user
            else:
                # for Admin, if organizer not chosen in form, default to self
                event.organizer = event.organizer or request.user
            event.save()
            messages.success(request, "Event created successfully.")
            return redirect("event-detail", event_id=event.id)
    else:
        form = EventForm()
    return render(request, "event_form.html", {"form": form, "title": "Create Event"})


@login_required
@user_passes_test(is_admin_or_organizer, login_url="no-permission")
def event_update(request, event_id):
    """
    Admin can edit anything.
    Organizer can only edit their own events.
    """
    event = get_object_or_404(Event, id=event_id)

    if not is_admin(request.user) and event.organizer_id != request.user.id:
        messages.error(request, "You can only edit your own events.")
        return redirect("no-permission")

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            updated = form.save(commit=False)
            if not is_admin(request.user):
                # keep organizer locked
                updated.organizer = request.user
            updated.save()
            messages.success(request, "Event updated successfully.")
            return redirect("event-detail", event_id=event.id)
    else:
        form = EventForm(instance=event)

    return render(request, "event_form.html", {"form": form, "title": "Update Event"})


@login_required
@user_passes_test(is_admin_or_organizer, login_url="no-permission")
def event_delete(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if not is_admin(request.user) and event.organizer_id != request.user.id:
        messages.error(request, "You can only delete your own events.")
        return redirect("no-permission")

    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully.")
        return redirect("event-list")

    # Optional: show a confirm page
    return render(request, "event_confirm_delete.html", {"event": event})


@login_required
@user_passes_test(is_participant, login_url="no-permission")
def event_rsvp(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    already = RSVP.objects.filter(user=request.user, event=event).exists()
    if already:
        messages.warning(request, "You already RSVP’d to this event.")
        return redirect("event-detail", event_id=event.id)

    RSVP.objects.create(user=request.user, event=event)
    messages.success(request, "RSVP successful! A confirmation email has been sent (if enabled).")
    return redirect("event-detail", event_id=event.id)


# -----------------------------------------
# Category CRUD (Admin & Organizer)
# -----------------------------------------
@login_required
@user_passes_test(is_admin_or_organizer, login_url="no-permission")
def category_list(request):
    categories = Category.objects.annotate(event_count=Count("event")).order_by("name")
    return render(request, "category_list.html", {"categories": categories})


@login_required
@user_passes_test(is_admin_or_organizer, login_url="no-permission")
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created.")
            return redirect("category-list")
    else:
        form = CategoryForm()
    return render(request, "category_form.html", {"form": form, "title": "Create Category"})


@login_required
@user_passes_test(is_admin_or_organizer, login_url="no-permission")
def category_update(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("category-list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "category_form.html", {"form": form, "title": "Update Category"})


@login_required
@user_passes_test(is_admin_or_organizer, login_url="no-permission")
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect("category-list")
    return render(request, "category_confirm_delete.html", {"category": category})
