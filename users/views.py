from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponse

# ----------------------------
# Helper: Admin check
# ----------------------------
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

# ----------------------------
# Signup with Email Activation
# ----------------------------

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Basic validations
        if not all([username, email, password, password2, first_name, last_name]):
            messages.error(request, "All fields are required")
            return redirect('signup')
        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('signup')

        # Create inactive user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False
        )

        messages.success(request, "Account created. Check your email to activate your account.")
        return redirect('login')

    return render(request, 'registration/signup.html')

   



# ----------------------------
# Activate Account
# ----------------------------
def activate_user(request, user_id, token):
    user = get_object_or_404(User, id=user_id)
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("login")
    return HttpResponse("Activation link is invalid or expired.")

# ----------------------------
# Login
# ----------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect('redirect-dashboard')
        else:
            messages.error(request, "Invalid credentials or inactive account.")
    return render(request, 'registration/login.html')


# ----------------------------
# Logout
# ----------------------------
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out.")
    return redirect('login')


# ----------------------------
# Role-based Redirection
# ----------------------------
@login_required
def redirect_dashboard(request):
    user = request.user
    if user.is_superuser or is_admin(user):
        return redirect('admin-dashboard')
    elif user.groups.filter(name='Organizer').exists():
        return redirect('organizer-dashboard')
    else:
        return redirect('participant-dashboard')


# ----------------------------
# Admin Dashboard View
# ----------------------------
@user_passes_test(is_admin, login_url='no-permission')
def admin_dashboard(request):
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()

    for user in users:
        user.group_name = user.all_groups[0].name if user.all_groups else "No Group Assigned"

    return render(request, 'admin/dashboard.html', {'users': users})


# ----------------------------
# Assign Role to User
# ----------------------------
@user_passes_test(is_admin, login_url='no-permission')
def assign_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        role_name = request.POST.get('role')
        group = Group.objects.get(name=role_name)
        user.groups.clear()
        user.groups.add(group)
        messages.success(request, f"{user.username} assigned to {role_name}.")
        return redirect('admin-dashboard')
    return render(request, 'admin/assign_role.html', {'user': user})


# ----------------------------
# Create Group
# ----------------------------
@user_passes_test(is_admin, login_url='no-permission')
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                messages.success(request, f"Group '{name}' created successfully.")
            else:
                messages.warning(request, f"Group '{name}' already exists.")
            return redirect('create-group')
    return render(request, 'admin/create_group.html')


# ----------------------------
# List Groups
# ----------------------------
@user_passes_test(is_admin, login_url='no-permission')
def group_list(request):
    groups = Group.objects.all().prefetch_related('permissions')
    return render(request, 'admin/group_list.html', {'groups': groups})
