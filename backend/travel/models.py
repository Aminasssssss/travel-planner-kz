from django.db import models
from django.contrib.auth.models import User


# Custom Manager
class PlaceManager(models.Manager):
    def by_category(self, category):
        return self.filter(category=category)

    def by_budget(self, level):
        return self.filter(price_level=level)

    def by_season(self, season):
        return self.filter(destination__season_best=season)


class Destination(models.Model):
    REGION_CHOICES = [
        ('almaty', 'Almaty'),
        ('astana', 'Astana'),
        ('shymkent', 'Shymkent'),
        ('turkestan', 'Turkestan'),
        ('aktau', 'Aktau'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    region = models.CharField(max_length=100, choices=REGION_CHOICES)
    description = models.TextField()
    season_best = models.CharField(max_length=50)  # e.g. 'summer', 'winter', 'all'
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('nature', 'Nature'),
        ('history', 'History'),
        ('food', 'Food'),
        ('active', 'Active'),
        ('photo', 'Photo Spots'),
    ]
    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Place(models.Model):
    BUDGET_CHOICES = [
        ('budget', 'Budget'),
        ('mid', 'Mid-range'),
        ('luxury', 'Luxury'),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_level = models.CharField(max_length=20, choices=BUDGET_CHOICES)
    open_hours = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    rating = models.FloatField(default=0.0)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='places')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='places')

    objects = PlaceManager()

    def __str__(self):
        return self.name


class Itinerary(models.Model):
    BUDGET_CHOICES = [
        ('budget', 'Budget'),
        ('mid', 'Mid-range'),
        ('luxury', 'Luxury'),
    ]
    title = models.CharField(max_length=200)
    duration_days = models.IntegerField()
    budget_level = models.CharField(max_length=20, choices=BUDGET_CHOICES)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='itineraries')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='itineraries')

    def __str__(self):
        return self.title


class ItineraryDay(models.Model):
    day_number = models.IntegerField()
    transport_note = models.CharField(max_length=300, blank=True)
    day_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='days')
    places = models.ManyToManyField(Place, related_name='days', blank=True)

    def __str__(self):
        return f"Day {self.day_number} of {self.itinerary.title}"


class PlaceReview(models.Model):
    rating = models.IntegerField()  # 1-5
    comment = models.TextField()
    visited_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=10, default='en')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='reviews')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.place.name}"


class SavedPlace(models.Model):
    note = models.CharField(max_length=300, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_places')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='saved_by')

    class Meta:
        unique_together = ('user', 'place')

    def __str__(self):
        return f"{self.user.username} saved {self.place.name}"