from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse

# ----------------------------
# Signup with Email Activation
# ----------------------------
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('signup')

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name, is_active=False
        )

        # Assign Participant role by default
        group, created = Group.objects.get_or_create(name='Participant')
        user.groups.add(group)

        # Send Activation Email
        current_site = get_current_site(request)
        subject = "Activate Your Account"
        message = render_to_string('registration/activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        messages.success(request, "Account created. Check your email to activate.")
        return redirect('login')

    return render(request, 'registration/signup.html')


# ----------------------------
# Activate Account
# ----------------------------
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated. You can now log in.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid or expired.")
        return redirect('home')


# ----------------------------
# Login View
# ----------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('redirect-dashboard')
            else:
                messages.warning(request, "Account not activated. Check your email.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'registration/login.html')


# ----------------------------
# Logout View
# ----------------------------
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')


# ----------------------------
# Redirect to Dashboard Based on Role
# ----------------------------
@login_required
def redirect_dashboard(request):
    user = request.user
    if user.is_superuser:
        return redirect('admin-dashboard')
    elif user.groups.filter(name='Organizer').exists():
        return redirect('organizer-dashboard')
    else:
        return redirect('participant-dashboard')


# ----------------------------
# Admin Only: Assign Role to User
# ----------------------------
@login_required
@permission_required('auth.change_group', raise_exception=True)
def assign_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        role = request.POST.get('role')
        group, created = Group.objects.get_or_create(name=role)
        user.groups.clear()
        user.groups.add(group)
        messages.success(request, f"{user.username} is now assigned to {role}.")
        return redirect('user-list')
    return render(request, 'admin/assign_role.html', {'user': user})
