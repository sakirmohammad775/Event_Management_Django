from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from events.models import Event

# in your home view
def home(request):
    user_groups = request.user.groups.values_list('name', flat=True) if request.user.is_authenticated else []
    return render(request, 'home.html', {'user_groups': user_groups})


# def home(request):
#     events = Event.objects.all().order_by('date')
#     return render(request, 'home.html',{'events':events})

def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')

def no_permission(request):
    return render(request, 'no_permission.html')
