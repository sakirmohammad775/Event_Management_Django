from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from events.models import Event

# in your home view
def home(request):
  return render(request,'home.html')



def no_permission(request):
    return render(request, 'no_permission.html')
