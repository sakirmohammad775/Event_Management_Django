import os
import django
import random
from faker import Faker

# Set environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "event_management.settings")
django.setup()

from events.models import Event, Category
from django.contrib.auth.models import User


fake = Faker()

def populate_db():
    # --- 1. Create Categories ---
    category_names = ['Technology', 'Health', 'Business', 'Art', 'Sports']
    categories = []
    for name in category_names:
        cat = Category.objects.create(
            name=name,
            description=fake.text(max_nb_chars=100)
        )
        categories.append(cat)
    print(f"✅ Created {len(categories)} categories.")

    # --- 2. Create Users (Participants & Organizers) ---
    participant_users = []
    organizer_users = []
    for i in range(10):
        user = User.objects.create_user(
            username=fake.user_name(),
            email=fake.email(),
            password='pass1234'
        )
        user.role = "participant"
        user.save()
        participant_users.append(user)

    for i in range(5):
        user = User.objects.create_user(
            username=fake.user_name(),
            email=fake.email(),
            password='pass1234'
        )
        user.role = "organizer"
        user.save()
        organizer_users.append(user)

    print(f"✅ Created {len(participant_users)} participants and {len(organizer_users)} organizers.")

    # --- 3. Create Events ---
    events = []
    for _ in range(15):
        organizer = random.choice(organizer_users)
        category = random.choice(categories)
        event = Event.objects.create(
            name=fake.catch_phrase(),
            description=fake.paragraph(nb_sentences=3),
            date=fake.date_this_year(before_today=False, after_today=True),
            time=fake.time(),
            location=fake.city(),
            category=category,
            organizer=organizer  # Assuming your Event model has an organizer field (ForeignKey to User)
        )
        # Add random participants as RSVPs
        rsvp_participants = random.sample(participant_users, random.randint(2, 6))
        for user in rsvp_participants:
            event.participants.add(user)

        events.append(event)

    print(f"✅ Created {len(events)} events and added RSVPs.")

    print("🎉 Database populated successfully!")


if __name__ == "__main__":
    populate_db()
