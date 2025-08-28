from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from events.models import Event

# in your home view
def home(request):
  events = Event.objects.all().order_by('-date')  # or filter upcoming events
  return render(request, 'home.html', {'events': events})


def no_permission(request):
    return render(request, 'no_permission.html')
