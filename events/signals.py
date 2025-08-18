from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import RSVP, Event

# ----------------------------
# Send account activation email when new user is created
# ----------------------------
@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        current_site = settings.SITE_DOMAIN if hasattr(settings, 'SITE_DOMAIN') else 'localhost:8000'
        subject = "Activate Your Event Management Account"
        message = render_to_string('registration/account_activation_email.html', {
            'user': instance,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(instance.pk)),
            'token': default_token_generator.make_token(instance),
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email], fail_silently=False)


# ----------------------------
# Send RSVP confirmation email when a participant RSVPs
# ----------------------------
@receiver(post_save, sender=RSVP)
def send_rsvp_email(sender, instance, created, **kwargs):
    if created:
        event = instance.event
        user = instance.user
        subject = f"RSVP Confirmation for {event.name}"
        message = render_to_string('events/rsvp_confirmation_email.html', {
            'user': user,
            'event': event,
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
