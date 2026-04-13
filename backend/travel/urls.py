from django.urls import path
from . import views

urlpatterns = [
    
    path('api/places/<int:place_id>/photo/', views.place_photo, name='place-photo'),
    path('api/destinations/<int:destination_id>/weather/', views.weather),
    path('api/ai/chat/', views.ai_chat),
    path('api/destinations/<int:destination_id>/clusters/', views.clustered_places),
    path('api/itineraries/<int:itinerary_id>/optimize/', views.optimize_itinerary),
    path('api/itineraries/<int:itinerary_id>/apply-optimization/', views.apply_optimization),
    path('api/itineraries/<int:itinerary_id>/burnout/', views.burnout_analysis),
    path('api/itineraries/<int:itinerary_id>/stats/', views.itinerary_stats),
    path('api/destinations/<int:pk>/', views.DestinationDetailView.as_view()),
    path('api/cities/<int:city_id>/events/', views.EventListView.as_view()),
    path('api/events/categories/', views.event_categories),
    path('api/itineraries/<int:itinerary_id>/add-place/', views.add_place_to_day),
    path('api/itineraries/<int:itinerary_id>/remove-place/', views.remove_place_from_day),
    path('api/itineraries/<int:itinerary_id>/move-place/', views.move_place),
]