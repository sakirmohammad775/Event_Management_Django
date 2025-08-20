from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from .models import RSVP, Event

# ----------------------------
# Send account activation email when new user is created
# ----------------------------
@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{instance.id}/{token}/"

        subject = "Activate Your Event Management Account"
        message = f"""Hi {instance.username},

Please activate your account by clicking the link below:
{activation_url}

Thank you!
"""
        recipient_list = [instance.email]

        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)
            print(f"Activation email sent to {instance.email}")
        except Exception as e:
            print(f"Failed to send activation email to {instance.email}: {str(e)}")


# ----------------------------
# Send RSVP confirmation email when a participant RSVPs
# ----------------------------
@receiver(post_save, sender=RSVP)
def send_rsvp_email(sender, instance, created, **kwargs):
    if created:
        event = instance.event
        user = instance.user
        subject = f"RSVP Confirmation for {event.name}"
        message = f"""Hi {user.username},

You have successfully RSVPed to the event: {event.name}.
Event Details:
- Date: {event.date}
- Time: {event.time}
- Location: {event.location}

Thank you!
"""
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
            print(f"RSVP confirmation email sent to {user.email}")
        except Exception as e:
            print(f"Failed to send RSVP email to {user.email}: {str(e)}")
