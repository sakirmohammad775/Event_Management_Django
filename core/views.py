from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from events.models import Event

# in your home view
def home(request):
    events = Event.objects.all()[:6]

    is_admin = request.user.is_superuser or request.user.groups.filter(name="Admin").exists() if request.user.is_authenticated else False
    is_organizer = request.user.groups.filter(name="Organizer").exists() if request.user.is_authenticated else False
    is_participant = request.user.groups.filter(name="Participant").exists() if request.user.is_authenticated else False

    return render(request, "home.html", {
        "events": events,
        "is_admin": is_admin,
        "is_organizer": is_organizer,
        "is_participant": is_participant,
    })


# def home(request):
#     events = Event.objects.all().order_by('date')
#     return render(request, 'home.html',{'events':events})

def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')

def no_permission(request):
    return render(request, 'no_permission.html')
