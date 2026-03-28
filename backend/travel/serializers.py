from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Destination, Category, Place, Itinerary, ItineraryDay, PlaceReview, SavedPlace



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PlaceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Place
        fields = ['id', 'name', 'description', 'price_level', 'open_hours',
                  'latitude', 'longitude', 'rating', 'destination', 'category', 'category_id']


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = '__all__'


class ItineraryDaySerializer(serializers.ModelSerializer):
    places = PlaceSerializer(many=True, read_only=True)

    class Meta:
        model = ItineraryDay
        fields = ['id', 'day_number', 'transport_note', 'day_cost', 'places']


class ItinerarySerializer(serializers.ModelSerializer):
    days = ItineraryDaySerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    destination = DestinationSerializer(read_only=True)
    destination_id = serializers.PrimaryKeyRelatedField(
        queryset=Destination.objects.all(), source='destination', write_only=True
    )

    class Meta:
        model = Itinerary
        fields = ['id', 'title', 'duration_days', 'budget_level', 'total_cost',
                  'is_public', 'created_at', 'user', 'destination', 'destination_id', 'days']


class PlaceReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PlaceReview
        fields = ['id', 'rating', 'comment', 'visited_date', 'language', 'user', 'place', 'created_at']


class SavedPlaceSerializer(serializers.ModelSerializer):
    place = PlaceSerializer(read_only=True)
    place_id = serializers.PrimaryKeyRelatedField(
        queryset=Place.objects.all(), source='place', write_only=True
    )

    class Meta:
        model = SavedPlace
        fields = ['id', 'note', 'added_at', 'place', 'place_id']



class ItineraryGenerateSerializer(serializers.Serializer):
    destination_id = serializers.IntegerField()
    duration_days = serializers.IntegerField(min_value=1, max_value=14)
    budget_level = serializers.ChoiceField(choices=['budget', 'mid', 'luxury'])
    interests = serializers.ListField(
        child=serializers.ChoiceField(choices=['nature', 'history', 'food', 'active', 'photo']),
        min_length=1
    )


class BudgetEstimateSerializer(serializers.Serializer):
    destination_id = serializers.IntegerField()
    duration_days = serializers.IntegerField(min_value=1)
    budget_level = serializers.ChoiceField(choices=['budget', 'mid', 'luxury'])
    num_people = serializers.IntegerField(min_value=1, default=1)