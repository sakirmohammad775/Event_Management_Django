from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from users.forms import AssignRoleForm

# ----------------------------
# Helper: Admin Check
# ----------------------------
def is_admin(user):
    return user.groups.filter(name='Admin').exists()

# ----------------------------
# Signup View
# ----------------------------
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Validation
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
        messages.success(request, "Account activated. You can login now.")
        return redirect("login")
    return render(request, 'no_permission.html', {"message": "Activation link invalid/expired."})


# ----------------------------
# Login & Logout
# ----------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect('redirect-dashboard')
        messages.error(request, "Invalid credentials or inactive account")
    return render(request, 'registration/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')


# ----------------------------
# Role-Based Dashboard Redirect
# ----------------------------
@login_required
def redirect_dashboard(request):
    user = request.user
    if user.is_superuser or is_admin(user):
        return redirect('admin-dashboard')
    elif user.groups.filter(name='Organizer').exists():
        return redirect('organizer-dashboard')
    elif user.groups.filter(name='Participant').exists():
        return redirect('participant-dashboard')
    else:
        messages.info(request, "You do not have a role assigned")
        return redirect('login')


# ----------------------------
# Admin Dashboard: Users
# ----------------------------
@user_passes_test(is_admin, login_url='no-permission')
def admin_dashboard(request):
    users = User.objects.prefetch_related('groups').all()
    for user in users:
        user.group_name = user.groups.first().name if user.groups.exists() else "No Group"
    return render(request, 'admin/dashboard.html', {'users': users})


# ----------------------------
# Assign Role to User
# ----------------------------
@user_passes_test(is_admin, login_url='no-permission')
def assign_role(request):
    form = AssignRoleForm(request.POST or None)
    message = ''
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        role = form.cleaned_data['role']
        user.groups.clear()
        user.groups.add(role)
        message = f"{user.username} assigned role: {role.name}"
    return render(request, 'admin/assign_role.html', {'form': form, 'message': message})


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
