from django.http import HttpResponseRedirect
from django.urls import reverse

def group_required(group_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse('login'))
            if not request.user.groups.filter(name=group_name).exists():
                return HttpResponseRedirect(reverse('no-permission'))
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
