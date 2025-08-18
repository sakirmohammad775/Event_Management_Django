from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

def default_event_image():
    return 'events_assets/default_img.jpg'

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='events_assets/', default=default_event_image)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    participants = models.ManyToManyField(User, through='RSVP', related_name='rsvped_events' ,blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.date})"

class RSVP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    rsvp_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} RSVP'd to {self.event.name}"
