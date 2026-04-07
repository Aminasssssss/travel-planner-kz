from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Destination, Place, Itinerary, ItineraryDay, PlaceReview, SavedPlace
from .serializers import (
    DestinationSerializer, PlaceSerializer, ItinerarySerializer,
    PlaceReviewSerializer, SavedPlaceSerializer,
    ItineraryGenerateSerializer, BudgetEstimateSerializer
)
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import NearestNeighbors



@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken'}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    return Response({'message': 'User created', 'id': user.id}, status=201)



class DestinationListView(generics.ListAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [AllowAny]


class DestinationPlacesView(generics.ListAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        destination_id = self.kwargs['pk']
        return Place.objects.filter(destination_id=destination_id)



class ItineraryListCreateView(generics.ListCreateAPIView):
    serializer_class = ItinerarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Itinerary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ItineraryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItinerarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Itinerary.objects.filter(user=self.request.user)



class SavedPlaceListCreateView(generics.ListCreateAPIView):
    serializer_class = SavedPlaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedPlace.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_itinerary(request):
    serializer = ItineraryGenerateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    data = serializer.validated_data
    destination_id = data['destination_id']
    duration_days = data['duration_days']
    budget_level = data['budget_level']
    interests = data['interests']

    try:
        destination = Destination.objects.get(id=destination_id)
    except Destination.DoesNotExist:
        return Response({'error': 'Destination not found'}, status=404)

    places_by_category = {}
    for interest in interests:
        places = list(Place.objects.filter(
            destination=destination,
            category__name=interest,
            price_level=budget_level
        ).order_by('-rating'))
        if places:
            places_by_category[interest] = places

    if not places_by_category:
        for interest in interests:
            places = list(Place.objects.filter(
                destination=destination,
                category__name=interest
            ).order_by('-rating'))
            if places:
                places_by_category[interest] = places

    if not places_by_category:
        all_places = list(Place.objects.filter(
            destination=destination
        ).order_by('-rating'))
        places_by_category['all'] = all_places

    used_place_ids = set()
    days_places = []

    category_keys = list(places_by_category.keys())
    places_per_day = 3

    for day_num in range(1, duration_days + 1):
        day_places = []

        for i in range(places_per_day):
            cat_key = category_keys[i % len(category_keys)]
            cat_places = places_by_category[cat_key]

            for place in cat_places:
                if place.id not in used_place_ids:
                    day_places.append(place)
                    used_place_ids.add(place.id)
                    break

        if len(day_places) < places_per_day:
            all_remaining = Place.objects.filter(
                destination=destination
            ).exclude(id__in=used_place_ids).order_by('-rating')[:places_per_day - len(day_places)]
            for place in all_remaining:
                day_places.append(place)
                used_place_ids.add(place.id)

        days_places.append(day_places)

    itinerary = Itinerary.objects.create(
        title=f"{duration_days}-day trip to {destination.name}",
        duration_days=duration_days,
        budget_level=budget_level,
        user=request.user,
        destination=destination,
        is_public=False
    )

    transport_notes = [
        'Taxi or public transport',
        'Walk or bike recommended',
        'Rent a car for this day',
        'Public bus available',
        'Uber or taxi recommended',
    ]

    for day_num, day_places in enumerate(days_places, 1):
        day = ItineraryDay.objects.create(
            itinerary=itinerary,
            day_number=day_num,
            transport_note=transport_notes[day_num % len(transport_notes)]
        )
        day.places.set(day_places)

    result = ItinerarySerializer(itinerary).data
    return Response(result, status=201)

@api_view(['GET'])
@permission_classes([AllowAny])
def popular_places(request):
    places = Place.objects.order_by('-rating')[:10]
    serializer = PlaceSerializer(places, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def recommend_places(request):
    place_id = request.query_params.get('place_id')
    destination_id = request.query_params.get('destination_id')
    
    if not destination_id:
        return Response({'error': 'destination_id required'}, status=400)

    places = list(Place.objects.filter(
        destination_id=destination_id
    ).select_related('category'))

    if len(places) < 3:
        serializer = PlaceSerializer(places, many=True)
        return Response(serializer.data)

    category_map = {'nature': 0, 'history': 1, 'food': 2, 'active': 3, 
                    'photo': 4, 'culture': 5, 'nightlife': 6, 'shopping': 7,
                    'family': 8, 'lifestyle': 9}
    budget_map = {'budget': 0, 'mid': 1, 'luxury': 2}

    features = []
    for p in places:
        cat = category_map.get(p.category.name if p.category else 'nature', 0)
        budget = budget_map.get(p.price_level, 0)
        features.append([
            cat,
            budget,
            float(p.rating),
            float(p.duration_hours),
            1 if p.is_indoor else 0,
        ])

    X = np.array(features)
    
    k = min(6, len(places) - 1)
    knn = NearestNeighbors(n_neighbors=k, metric='euclidean')
    knn.fit(X)

    if place_id:
        try:
            target = Place.objects.get(id=place_id)
            target_idx = next(i for i, p in enumerate(places) if p.id == target.id)
            distances, indices = knn.kneighbors([X[target_idx]])
            recommended = [places[i] for i in indices[0][1:]]
        except (Place.DoesNotExist, StopIteration):
            recommended = places[:5]
    else:
        recommended = sorted(places, key=lambda p: p.rating, reverse=True)[:6]

    serializer = PlaceSerializer(recommended, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def budget_estimate(request):
    serializer = BudgetEstimateSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    data = serializer.validated_data
    duration = data['duration_days']
    level = data['budget_level']
    people = data['num_people']

    rates = {'budget': 5000, 'mid': 15000, 'luxury': 40000}
    daily = rates.get(level, 10000)
    total = daily * duration * people

    return Response({
        'duration_days': duration,
        'budget_level': level,
        'num_people': people,
        'daily_estimate_tenge': daily,
        'total_estimate_tenge': total
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, place_id):
    try:
        place = Place.objects.get(id=place_id)
    except Place.DoesNotExist:
        return Response({'error': 'Place not found'}, status=404)

    serializer = PlaceReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, place=place)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)