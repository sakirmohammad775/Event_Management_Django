from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def assign_participant_role(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name='Participant')
        instance.groups.add(group)
