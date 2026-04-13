from django.db import models
from django.contrib.auth.models import User
import uuid


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
    region = models.CharField(max_length=100)   
    description = models.TextField()
    season_best = models.CharField(max_length=50) 
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
        ('culture', 'Culture'),
        ('nightlife', 'Nightlife'),
        ('shopping', 'Shopping'),
        ('family', 'Family'),
        ('lifestyle', 'Lifestyle'),
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
    price_tenge = models.IntegerField(default=0)
    best_season = models.CharField(max_length=100, blank=True)
    duration_hours = models.FloatField(default=2.0)
    tags = models.CharField(max_length=300, blank=True)
    is_indoor = models.BooleanField(default=False)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='places')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='places')
    photo_url = models.URLField(blank=True, null=True)
    photo_credit = models.CharField(max_length=200, blank=True)
    photo_updated = models.DateTimeField(null=True, blank=True)

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
    share_token = models.UUIDField(default=uuid.uuid4, null=True, blank=True)  # без unique
    is_public = models.BooleanField(default=False)
    def __str__(self):
        return self.title


class ItineraryDay(models.Model):
    day_number = models.IntegerField()
    transport_note = models.CharField(max_length=300, blank=True)
    day_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='days')
    places = models.ManyToManyField(Place, through='ItineraryDayPlace', related_name='days', blank=True)
    def __str__(self):
        return f"Day {self.day_number} of {self.itinerary.title}"


class PlaceReview(models.Model):
    rating = models.IntegerField()  
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

class ItineraryDayPlace(models.Model):
    day = models.ForeignKey('ItineraryDay', on_delete=models.CASCADE)
    place = models.ForeignKey('Place', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ('day', 'place')


class Event(models.Model):
    CATEGORY_CHOICES = [
        ('concert', '🎵 Концерт'),
        ('theatre', '🎭 Театр'),
        ('masterclass', '🎨 Мастер-класс'),
        ('food', '🍽️ Гастро'),
        ('sport', '🏃 Спорт'),
        ('kids', '👶 Детям'),
        ('exhibition', '🖼️ Выставка'),
        ('party', '🎉 Вечеринка'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    city = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='events')
    location = models.CharField(max_length=300)
    address = models.CharField(max_length=500, blank=True)
    
    date = models.DateField()
    time = models.TimeField()
    
    price_from = models.IntegerField(default=0)
    ticket_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    
    is_sponsored = models.BooleanField(default=False)
    sponsor_label = models.CharField(max_length=50, blank=True, default='Партнёр')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_sponsored', 'date', 'time']
    
    def __str__(self):
        return f"{self.title} - {self.city.name}"