from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from .models import Event, Category, RSVP
from .forms import EventForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

def is_admin_or_organizer(user):
    return user.is_superuser or user.groups.filter(name__in=['Admin', 'Organizer']).exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()


# Organizer Dashboard
@user_passes_test(is_organizer, login_url='no-permission')
def organizer_dashboard(request):
    events = Event.objects.filter(
        organizer=request.user 
    ).select_related('category').prefetch_related('participants')

    total_events = events.count()
    upcoming_events = events.filter(date__gte=date.today()).count()
    past_events = events.filter(date__lt=date.today()).count()
    total_participants = RSVP.objects.filter(event__organizer=request.user).count()
    today_events = events.filter(date=date.today())

    context = {
        'events': events,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'total_participants': total_participants,
        'today_events': today_events,
    }
    return render(request, 'dashboard/organizer_dashboard.html', context)

# Participant Dashboard
@user_passes_test(is_participant, login_url='no-permission')
def participant_dashboard(request):
    rsvps = RSVP.objects.filter(user=request.user).select_related('event', 'event__category')
    events = [rsvp.event for rsvp in rsvps]
    return render(request, 'dashboard/participant_dashboard.html', {'events': events})

# Event List (all users)
@login_required
def event_list(request):
    events = Event.objects.select_related('category').annotate(rsvp_count=Count('participants'))
    # Optional: filter by category or search
    category_id = request.GET.get('category')
    search = request.GET.get('search')
    if category_id:
        events = events.filter(category_id=category_id)
    if search:
        events = events.filter(name__icontains=search)
    return render(request, 'events/event_list.html', {'events': events})

# Event Detail
def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "event_details.html", {"event": event})

# Create / Update Event
@user_passes_test(is_organizer, login_url='no-permission')
def event_form(request, event_id=None):
    if event_id:
        event = get_object_or_404(Event, id=event_id, organizer=request.user)
    else:
        event = None
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        date = request.POST['date']
        time = request.POST['time']
        location = request.POST['location']
        category_id = request.POST['category']
        image = request.FILES.get('image')
        category = get_object_or_404(Category, id=category_id)
        if event:
            # Update
            event.name = name
            event.description = description
            event.date = date
            event.time = time
            event.location = location
            event.category = category
            if image:
                event.image = image
            event.save()
            messages.success(request, "Event updated")
        else:
            # Create
            Event.objects.create(
                name=name,
                description=description,
                date=date,
                time=time,
                location=location,
                category=category,
                organizer=request.user,
                image=image if image else 'events_assets/default_img.jpg'
            )
            messages.success(request, "Event created")
        return redirect('organizer-dashboard')
    categories = Category.objects.all()
    return render(request, 'events/event_form.html', {'event': event, 'categories': categories})

# RSVP to Event
@user_passes_test(is_participant, login_url='no-permission')
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    rsvp, created = RSVP.objects.get_or_create(user=request.user, event=event)
    if created:
        messages.success(request, f"RSVP successful for {event.name}")
    else:
        messages.info(request, f"You already RSVPed to {event.name}")
    return redirect('participant-dashboard')


#Event Delete
@login_required
@user_passes_test(is_admin_or_organizer, login_url="login")
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect("event-list")
    return render(request, "events/event_confirm_delete.html", {"event": event})

#Event Update
@login_required
@user_passes_test(is_admin_or_organizer, login_url="login")
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect("organizer-dashboard")  # change to your dashboard url name
    else:
        form = EventForm(instance=event)

    return render(request, "event_form.html", {"form": form})

@login_required
@user_passes_test(is_admin_or_organizer, login_url="login")
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user  # logged-in user as organizer
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect("organizer-dashboard")
    else:
        form = EventForm()
    
    return render(request, "event_create.html", {"form": form})
# --- Event CRUD ---
@login_required
def event_list(request):
    events = Event.objects.select_related("category", "organizer").all()
    return render(request, "events/event_list.html", {"events": events})


###########Category
from .models import Category
from .forms import CategoryForm


# --- Category CRUD ---
@login_required
@user_passes_test(is_admin_or_organizer, login_url="login")
def category_list(request):
    categories = Category.objects.all()
    return render(request, "events/category_list.html", {"categories": categories})


@login_required
@user_passes_test(is_admin_or_organizer, login_url="login")
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully!")
            return redirect("category-list")
    else:
        form = CategoryForm()
    return render(request, "events/category_form.html", {"form": form})


@login_required
@user_passes_test(is_admin_or_organizer, login_url="login")
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect("category-list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "events/category_form.html", {"form": form, "category": category})


@login_required
@user_passes_test(is_admin_or_organizer, login_url="login")
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "Category deleted successfully!")
        return redirect("category-list")
    return render(request, "events/category_confirm_delete.html", {"category": category})


##Class based views.....
# ----------------------------
# Event List (CBV)
# ----------------------------
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        queryset = Event.objects.select_related('category', 'organizer').all()
        category_id = self.request.GET.get('category')
        search = self.request.GET.get('search')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


# ----------------------------
# Category List (CBV)
# ----------------------------
class CategoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = 'events/category_list.html'
    context_object_name = 'categories'

    def test_func(self):
        return is_admin_or_organizer(self.request.user)


# ----------------------------
# Category Create (CBV)
# ----------------------------
class CategoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    success_url = reverse_lazy('category-list')

    def test_func(self):
        return is_admin_or_organizer(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Category created successfully!")
        return super().form_valid(form)


# ----------------------------
# Category Update (CBV)
# ----------------------------
class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/category_form.html'
    success_url = reverse_lazy('category-list')

    def test_func(self):
        return is_admin_or_organizer(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully!")
        return super().form_valid(form)


# ----------------------------
# Category Delete (CBV)
# ----------------------------

class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    template_name = 'events/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')

    def test_func(self):
        return is_admin_or_organizer(self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Category deleted successfully!")
        return super().delete(request, *args, **kwargs)
# List Categories
@login_required
@user_passes_test(is_admin_or_organizer, login_url='login')
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'events/category_list.html', {'categories': categories})

# Add Category
@login_required
@user_passes_test(is_admin_or_organizer, login_url='login')
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        if name:
            category.name = name
            category.description = description
            category.save()
            messages.success(request, f"Category '{name}' updated successfully!")
            return redirect('category-list')
        else:
            messages.error(request, "Category name cannot be empty.")

    return render(request, 'events/category_form.html', {'category': category})