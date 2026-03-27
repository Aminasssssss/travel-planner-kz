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


# ── AUTH ──────────────────────────────────────────────────────────

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


# ── CBV: Destinations ─────────────────────────────────────────────

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


# ── CBV: Itineraries ──────────────────────────────────────────────

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


# ── CBV: Saved Places ─────────────────────────────────────────────

class SavedPlaceListCreateView(generics.ListCreateAPIView):
    serializer_class = SavedPlaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedPlace.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ── FBV: Generate Itinerary ───────────────────────────────────────

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

    # Get places matching interests and budget
    places = Place.objects.filter(
        destination=destination,
        price_level=budget_level,
        category__name__in=interests
    )

    if not places.exists():
        places = Place.objects.filter(destination=destination)

    places = list(places)
    places_per_day = 3

    # Create itinerary
    itinerary = Itinerary.objects.create(
        title=f"{duration_days}-day trip to {destination.name}",
        duration_days=duration_days,
        budget_level=budget_level,
        user=request.user,
        destination=destination,
        is_public=False
    )

    # Assign places to days
    for day_num in range(1, duration_days + 1):
        day = ItineraryDay.objects.create(
            itinerary=itinerary,
            day_number=day_num,
            transport_note='Taxi or public transport'
        )
        start = (day_num - 1) * places_per_day
        end = start + places_per_day
        day_places = places[start:end] if start < len(places) else places[:places_per_day]
        day.places.set(day_places)

    result = ItinerarySerializer(itinerary).data
    return Response(result, status=201)


# ── FBV: Popular Places ───────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def popular_places(request):
    places = Place.objects.order_by('-rating')[:10]
    serializer = PlaceSerializer(places, many=True)
    return Response(serializer.data)


# ── FBV: Budget Estimate ──────────────────────────────────────────

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


# ── FBV: Create Review ────────────────────────────────────────────

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