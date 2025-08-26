from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{instance.id}/{token}/"

        subject = 'Activate Your Account'
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
            print(f"Failed to send email to {instance.email}: {str(e)}")

def assign_default_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name='Participant')
        instance.groups.add(group)
        # No need to call instance.save() here
