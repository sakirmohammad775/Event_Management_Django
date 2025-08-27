from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.core.mail import send_mail
from django.contrib import messages
from django.db.models import Prefetch
from django.http import HttpResponse

from .forms import AssignRoleForm
from events.models import Category   # ✅ for category_list


# ----------------------------
# Helper: Admin check
# ----------------------------
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()


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

        if not all([username, email, password, password2, first_name, last_name]):
            messages.error(request, "All fields are required")
            return redirect('signup')
        if password != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False
        )
        messages.success(request, "Account created. Please ask admin to activate your account.")
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
    if is_admin(user):
        return redirect('admin-dashboard')
    elif user.groups.filter(name='Organizer').exists():
        return redirect('organizer-dashboard')
    elif user.groups.filter(name='Participant').exists():
        return redirect('participant-dashboard')
    else:
        messages.info(request, "Please ask admin to assign a role.")
        return redirect('login')


# ----------------------------
# Admin Dashboard
# ----------------------------
@user_passes_test(is_admin, login_url='no-permission')
def admin_dashboard(request):
    # Prefetch groups for efficiency
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()

    # Add a readable group name field
    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = "No Group Assigned"

    return render(request, "admin/dashboard.html", {"users": users})

# ----------------------------
# Assign Role to User
# ----------------------------
@user_passes_test(is_admin, login_url='login')
def assign_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = AssignRoleForm(request.POST or None, initial={'user': user})
    if request.method == 'POST' and form.is_valid():
        role = form.cleaned_data['role']
        user.groups.clear()
        user.groups.add(role)
        messages.success(request, f"{user.username} has been assigned role: {role.name}")
        return redirect('user-list')

    return render(request, 'admin/assign_role.html', {'form': form, 'user': user})


# ----------------------------
# Create Group
# ----------------------------
@user_passes_test(is_admin, login_url='login')
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                messages.success(request, f"Group '{name}' created successfully.")
            else:
                messages.warning(request, f"Group '{name}' already exists.")
            return redirect('group-list')
    return render(request, 'admin/create_group.html')


# ----------------------------
# List Groups
# ----------------------------
@user_passes_test(is_admin, login_url='login')
def group_list(request):
    groups = Group.objects.all().prefetch_related('permissions')
    return render(request, 'admin/group_list.html', {'groups': groups})


# ----------------------------
# List Users
# ----------------------------
@user_passes_test(is_admin, login_url='login')
def user_list(request):
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()
    for user in users:
        user.group_name = user.all_groups[0].name if user.all_groups else "No Group Assigned"
    return render(request, 'admin/user_list.html', {'users': users})


# ----------------------------
# Category List (Admin only)
# ----------------------------
@user_passes_test(is_admin, login_url='login')
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'admin/category_list.html', {'categories': categories})


@login_required
def redirect_dashboard(request):
    user = request.user
    if is_admin(user):
        return redirect('admin-dashboard')
    elif user.groups.filter(name='Organizer').exists():
        return redirect('organizer-dashboard')
    elif user.groups.filter(name='Participant').exists():
        return redirect('participant-dashboard')
    else:
        messages.info(request, "Please activate your account or ask admin to assign a role.")
        return redirect('login')
