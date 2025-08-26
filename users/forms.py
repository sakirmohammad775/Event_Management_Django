from django import forms
from django.contrib.auth.models import User, Group, Permission

class AssignRoleForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        empty_label="Select a User"
    )
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        empty_label="Select a Role"
    )

class CreateGroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Assign Permissions'
    )

    class Meta:
        model = Group
        fields = ('name', 'permissions')
