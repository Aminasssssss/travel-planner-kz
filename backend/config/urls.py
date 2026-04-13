from django.contrib import admin
from django.urls import path, include 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from travel import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('travel.urls')), 

    path('api/auth/register/', views.register),
    path('api/auth/login/', TokenObtainPairView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view()),

    path('api/destinations/', views.DestinationListView.as_view()),
    path('api/destinations/<int:pk>/places/', views.DestinationPlacesView.as_view()),

    path('api/places/popular/', views.popular_places),
    path('api/places/<int:place_id>/reviews/', views.create_review),

    path('api/itineraries/', views.ItineraryListCreateView.as_view()),
    path('api/itineraries/<int:pk>/', views.ItineraryDetailView.as_view()),
    path('api/itineraries/generate/', views.generate_itinerary),

    path('api/saved-places/', views.SavedPlaceListCreateView.as_view()),

    path('api/budget/estimate/', views.budget_estimate),
    path('api/places/recommend/', views.recommend_places),
    path('api/itineraries/<int:itinerary_id>/share/', views.share_itinerary),
    path('api/itineraries/<int:itinerary_id>/unshare/', views.unshare_itinerary),
    path('api/shared/<uuid:share_token>/', views.view_shared_itinerary),
]