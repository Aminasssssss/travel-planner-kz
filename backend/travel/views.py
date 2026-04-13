from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Destination, Place, Itinerary, ItineraryDay, PlaceReview, SavedPlace, ItineraryDayPlace, Event
from .serializers import (
    DestinationSerializer, PlaceSerializer, ItinerarySerializer,
    PlaceReviewSerializer, SavedPlaceSerializer,
    ItineraryGenerateSerializer, BudgetEstimateSerializer
)

from .ml.tsp_solver import GeneticTSP
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import NearestNeighbors
from .ml.clustering import PlaceClusterer
from django.core.cache import cache
import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .ml.ai_guide import AITravelGuide
from django.conf import settings
from .models import Event
from .serializers import EventSerializer
from django.utils import timezone
from django.db.models import Count  
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
        queryset = Place.objects.filter(destination_id=destination_id)
        
        price = self.request.query_params.get('price')
        if price == 'budget':
            queryset = queryset.filter(price_level='budget')
        elif price == 'premium':
            queryset = queryset.filter(price_level='luxury')
        elif price == 'free':
            queryset = queryset.filter(price_tenge=0)
        
        indoor = self.request.query_params.get('indoor')
        if indoor == 'true':
            queryset = queryset.filter(is_indoor=1)  # ← 1, не True
        elif indoor == 'false':
            queryset = queryset.filter(is_indoor=0)  # ← 0, не False
        
        top = self.request.query_params.get('top')
        if top:
            queryset = queryset.order_by('-rating')[:int(top)]
        
        duration = self.request.query_params.get('duration')
        if duration == 'quick':
            queryset = queryset.filter(duration_hours__lt=1)
        elif duration == 'halfday':
            queryset = queryset.filter(duration_hours__gte=3, duration_hours__lte=4)
        elif duration == 'fullday':
            queryset = queryset.filter(duration_hours__gt=6)
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name=category)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset

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
    places_per_day = min(7, max(4, len(interests) * 2))
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
        for order, place in enumerate(day_places):
            ItineraryDayPlace.objects.create(day=day, place=place, order=order)

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

import uuid

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_itinerary(request, itinerary_id):
    try:
        itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
        if not itinerary.share_token:
            itinerary.share_token = uuid.uuid4()
        itinerary.is_public = True
        itinerary.save()
        return Response({
            'share_url': f'/shared/itinerary/{itinerary.share_token}',
            'is_public': True
        })
    except Itinerary.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unshare_itinerary(request, itinerary_id):
    try:
        itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
        itinerary.is_public = False
        itinerary.save()
        return Response({'is_public': False})
    except Itinerary.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def view_shared_itinerary(request, share_token):
    try:
        itinerary = Itinerary.objects.get(share_token=share_token, is_public=True)
        serializer = ItinerarySerializer(itinerary)
        return Response(serializer.data)
    except Itinerary.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def place_photo(request, place_id):
    try:
        place = Place.objects.get(id=place_id)
        
        if place.photo_url and place.photo_updated:
            if timezone.now() - place.photo_updated < timedelta(days=7):
                return Response({
                    'url': place.photo_url,
                    'credit': place.photo_credit
                })
        
        query = f"{place.name} {place.destination.name} Kazakhstan"
        response = requests.get(
            'https://api.unsplash.com/search/photos',
            params={'query': query, 'per_page': 1, 'orientation': 'landscape'},
            headers={'Authorization': f'Client-ID {settings.UNSPLASH_ACCESS_KEY}'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                place.photo_url = data['results'][0]['urls']['regular']
                place.photo_credit = data['results'][0]['user']['name']
                place.photo_updated = timezone.now()
                place.save()
                
                return Response({
                    'url': place.photo_url,
                    'credit': place.photo_credit
                })
        
        return Response({'url': None, 'fallback': True})
    except:
        return Response({'url': None, 'fallback': True})
    
@api_view(['GET'])
@permission_classes([AllowAny])
def weather(request, destination_id):
    try:
        destination = Destination.objects.get(id=destination_id)
        
        response = requests.get(
            'https://api.openweathermap.org/data/2.5/weather',
            params={
                'q': f"{destination.name},KZ",
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric',
                'lang': 'ru'
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            temp = round(data['main']['temp'])
            
            if temp < 0:
                recommendation = "❄️ Холодно! Возьмите тёплую куртку"
            elif temp < 10:
                recommendation = "🌬️ Прохладно. Наденьте куртку"
            elif temp < 20:
                recommendation = "🌸 Комфортно. Лёгкая куртка"
            elif temp < 30:
                recommendation = "☀️ Тепло. Идеально для прогулок"
            else:
                recommendation = "🔥 Жарко! Не забудьте воду"
            
            return Response({
                'temp': temp,
                'feels_like': round(data['main']['feels_like']),
                'description': data['weather'][0]['description'].capitalize(),
                'icon': f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
                'humidity': data['main']['humidity'],
                'wind': round(data['wind']['speed'], 1),
                'recommendation': recommendation
            })
        
        return Response({'error': 'Weather unavailable'}, status=500)
    except Exception as e:
        return Response({'error': 'Weather unavailable'}, status=500)
@api_view(['POST'])
@permission_classes([AllowAny])
def ai_chat(request):
    question = request.data.get('question', '').strip()
    destination_id = request.data.get('destination_id')
    
    if not question:
        return Response({'error': 'Question required'}, status=400)
    
    if len(question) < 3:
        return Response({'answer': 'Задайте вопрос подробнее, я постараюсь помочь!'})
    
    try:
        if destination_id:
            destination = Destination.objects.get(id=destination_id)
            places = Place.objects.filter(destination=destination)[:5]
            destination_name = destination.name
        else:
            places = Place.objects.all()[:5]
            destination_name = 'Казахстан'
        
        guide = AITravelGuide(api_key=settings.GEMINI_API_KEY)
        answer = guide.ask(question, places, destination_name)
        
        return Response({'answer': answer})
    except Destination.DoesNotExist:
        return Response({'answer': 'Город не найден. Уточните название.'})
    except Exception as e:
        print(f"AI Chat error: {e}")
        return Response({'answer': 'Извините, произошла ошибка. Попробуйте позже.'})

@api_view(['GET'])
@permission_classes([AllowAny])
def clustered_places(request, destination_id):
    cache_key = f'clusters_{destination_id}'
    cached = cache.get(cache_key)
    if cached:
        return Response(cached)
    
    try:
        places = Place.objects.filter(destination_id=destination_id)
        
        if not places.exists():
            return Response({'error': 'No places found'}, status=404)
        
        clusterer = PlaceClusterer(places)
        clusters = clusterer.cluster_places(n_clusters=4)
        
        result = {}
        for cluster_name, place_ids in clusters.items():
            cluster_places = Place.objects.filter(id__in=place_ids)
            result[cluster_name] = PlaceSerializer(cluster_places, many=True).data
        
        cache.set(cache_key, result, 3600)
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def optimize_itinerary(request, itinerary_id):
    try:
        itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
        
        days_places = []
        for day in itinerary.days.all().order_by('day_number'):
            places = list(day.places.all().order_by('itinerarydayplace__order'))
            if places:
                days_places.append(places)
        
        if not days_places:
            return Response({'error': 'No places in itinerary'}, status=400)
        
        result = GeneticTSP().optimize_per_day(days_places)
        return Response(result)
        
    except Itinerary.DoesNotExist:
        return Response({'error': 'Itinerary not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_optimization(request, itinerary_id):
    try:
        from .models import ItineraryDayPlace
        
        itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
        optimized_order = request.data.get('optimized_order', [])
        
        if not optimized_order:
            return Response({'error': 'No optimized order provided'}, status=400)
        
        for day_data in optimized_order:
            day = itinerary.days.filter(day_number=day_data['day']).first()
            if day:
                ItineraryDayPlace.objects.filter(day=day).delete()
                for order, place_data in enumerate(day_data['places']):
                    place = Place.objects.get(id=place_data['id'])
                    ItineraryDayPlace.objects.create(
                        day=day,
                        place=place,
                        order=order
                    )
        
        return Response({'success': True})
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def burnout_analysis(request, itinerary_id):
    try:
        itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
        days_analysis = []
        total_places = 0
        total_hours = 0
        total_distance = 0

        for day in itinerary.days.all().order_by('day_number'):
            places = list(day.places.all().order_by('itinerarydayplace__order'))
            places_count = len(places)
            day_hours = sum(p.duration_hours or 2 for p in places)

            day_distance = 0
            for i in range(len(places) - 1):
                day_distance += haversine(
                    places[i].latitude, places[i].longitude,
                    places[i+1].latitude, places[i+1].longitude
                )

            if day_hours > 16:
                level = 'overload'
                icon = '🔴'
                recommendation = 'Слишком насыщенный день'
            elif day_hours > 12:
                level = 'medium'
                icon = '🟡'
                recommendation = 'Плотный график, но выполнимо'
            else:
                level = 'optimal'
                icon = '🟢'
                recommendation = None

            days_analysis.append({
                'day_number': day.day_number,
                'places_count': places_count,
                'hours': round(day_hours, 1),
                'distance_km': round(day_distance, 1),
                'level': level,
                'icon': icon,
                'recommendation': recommendation,
                'places': PlaceSerializer(places, many=True).data
            })

            total_places += places_count
            total_hours += day_hours
            total_distance += day_distance

        avg_hours = total_hours / len(days_analysis)
        overloaded_days = sum(1 for d in days_analysis if d['level'] == 'overload')

        if overloaded_days >= 2:
            overall = '⚠️ Маршрут перегружен! Рекомендуем сократить количество активностей или увеличить количество дней.'
        elif overloaded_days == 1:
            overall = '⚡ Один день перегружен. Рекомендуем перераспределить активности.'
        elif avg_hours > 14:
            overall = '📊 Маршрут очень плотный. Следите за усталостью.'
        else:
            overall = '✅ Хорошо сбалансированный маршрут!'

        return Response({
            'days': days_analysis,
            'total_places': total_places,
            'total_hours': round(total_hours, 1),
            'total_distance_km': round(total_distance, 1),
            'avg_hours_per_day': round(avg_hours, 1),
            'overall_recommendation': overall
        })

    except Itinerary.DoesNotExist:
        return Response({'error': 'Itinerary not found'}, status=404)
    
class DestinationDetailView(generics.RetrieveAPIView):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [AllowAny]

class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        city_id = self.kwargs.get('city_id')
        today = timezone.now().date()
        
        queryset = Event.objects.filter(
            city_id=city_id,
            date__gte=today
        )
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset

@api_view(['GET'])
@permission_classes([AllowAny])
def event_categories(request):
    city_id = request.query_params.get('city_id')
    today = timezone.now().date()
    
    counts = Event.objects.filter(
        city_id=city_id,
        date__gte=today
    ).values('category').annotate(count=Count('id'))
    
    label_map = dict(Event.CATEGORY_CHOICES)
    categories = {}
    
    for item in counts:
        cat = item['category']
        categories[cat] = {
            'label': label_map[cat],
            'count': item['count']
        }
    
    return Response(categories)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def itinerary_stats(request, itinerary_id):
    try:
        import math
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
        
        all_places = []
        for day in itinerary.days.all():
            all_places.extend(day.places.all().order_by('itinerarydayplace__order'))
        
        if not all_places:
            return Response({'error': 'No places'}, status=400)
        
        categories = {}
        for place in all_places:
            cat = place.category.name if place.category else 'other'
            categories[cat] = categories.get(cat, 0) + 1
        
        indoor = sum(1 for p in all_places if p.is_indoor)
        outdoor = len(all_places) - indoor
        total_budget = sum(p.price_tenge or 0 for p in all_places)
        avg_rating = sum(p.rating or 0 for p in all_places) / len(all_places)
        total_hours = sum(p.duration_hours or 2 for p in all_places)
        
        current_month = timezone.now().month
        season_match = 0
        for p in all_places:
            if not p.best_season:
                season_match += 1
                continue
            best = p.best_season.lower()
            if best in ['all', 'круглый год', 'все сезоны']:
                season_match += 1
            elif best in ['summer', 'лето'] and current_month in [6,7,8]:
                season_match += 1
            elif best in ['winter', 'зима'] and current_month in [12,1,2]:
                season_match += 1
            elif best in ['spring', 'весна'] and current_month in [3,4,5]:
                season_match += 1
            elif best in ['autumn', 'осень'] and current_month in [9,10,11]:
                season_match += 1
        
        season_match_percent = round((season_match / len(all_places)) * 100)
        
        high_demand = sum(1 for p in all_places if p.rating and p.rating >= 4.7)
        medium_demand = sum(1 for p in all_places if p.rating and 4.3 <= p.rating < 4.7)
        low_demand = len(all_places) - high_demand - medium_demand
        
        total_distance = 0
        for day in itinerary.days.all():
            places_list = list(day.places.all().order_by('itinerarydayplace__order'))
            for i in range(len(places_list) - 1):
                total_distance += haversine(
                    places_list[i].latitude, places_list[i].longitude,
                    places_list[i+1].latitude, places_list[i+1].longitude
                )
        
        total_steps = int(total_distance * 1000 * 1.3)
        
        morning = sum(1 for p in all_places if p.open_hours and '09' in p.open_hours)
        day_time = sum(1 for p in all_places if p.open_hours and '12' in p.open_hours)
        evening = sum(1 for p in all_places if p.open_hours and ('18' in p.open_hours or '19' in p.open_hours))
        
        return Response({
            'total_places': len(all_places),
            'total_budget': total_budget,
            'avg_rating': round(avg_rating, 1),
            'total_hours': round(total_hours, 1),
            'categories': categories,
            'indoor_count': indoor,
            'outdoor_count': outdoor,
            'open_count': len(all_places),
            'closed_count': 0,
            'parking_yes': 0,
            'parking_no': 0,
            'parking_coming_soon': True,
            'season_match': season_match,
            'season_match_percent': season_match_percent,
            'current_season': _get_current_season(current_month),
            'high_demand': high_demand,
            'medium_demand': medium_demand,
            'low_demand': low_demand,
            'total_steps': total_steps,
            'total_distance_km': round(total_distance, 1),
            'morning_places': morning,
            'day_places_count': day_time,
            'evening_places': evening,
        })
        
    except Itinerary.DoesNotExist:
        return Response({'error': 'Itinerary not found'}, status=404)
    
def _get_current_season(month):
    if month in [12, 1, 2]: return 'Зима'
    elif month in [3, 4, 5]: return 'Весна'
    elif month in [6, 7, 8]: return 'Лето'
    else: return 'Осень'

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_place_to_day(request, itinerary_id):
    try:
        day_number = request.data.get('day_number')
        place_id = request.data.get('place_id')
        
        itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
        day = itinerary.days.get(day_number=day_number)
        place = Place.objects.get(id=place_id)
        
        last_order = ItineraryDayPlace.objects.filter(day=day).count()
        ItineraryDayPlace.objects.create(day=day, place=place, order=last_order)
        
        return Response({'success': True})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_place_from_day(request, itinerary_id):
    try:
        day_number = request.data.get('day_number')
        place_id = request.data.get('place_id')
        
        itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
        day = itinerary.days.get(day_number=day_number)
        
        ItineraryDayPlace.objects.filter(day=day, place_id=place_id).delete()
        
        for new_order, item in enumerate(ItineraryDayPlace.objects.filter(day=day).order_by('order')):
            item.order = new_order
            item.save()
        
        return Response({'success': True})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_place(request, itinerary_id):
    try:
        from_day = request.data.get('from_day')
        to_day = request.data.get('to_day')
        place_id = request.data.get('place_id')
        
        itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
        
        day_from = itinerary.days.get(day_number=from_day)
        ItineraryDayPlace.objects.filter(day=day_from, place_id=place_id).delete()
        
        day_to = itinerary.days.get(day_number=to_day)
        last_order = ItineraryDayPlace.objects.filter(day=day_to).count()
        ItineraryDayPlace.objects.create(day=day_to, place_id=place_id, order=last_order)
        
        return Response({'success': True})
    except Exception as e:
        return Response({'error': str(e)}, status=500)