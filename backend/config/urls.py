from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from travel import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/auth/register/', views.register),
    path('api/auth/login/', TokenObtainPairView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view()),

    # Destinations
    path('api/destinations/', views.DestinationListView.as_view()),
    path('api/destinations/<int:pk>/places/', views.DestinationPlacesView.as_view()),

    # Places
    path('api/places/popular/', views.popular_places),
    path('api/places/<int:place_id>/reviews/', views.create_review),

    # Itineraries
    path('api/itineraries/', views.ItineraryListCreateView.as_view()),
    path('api/itineraries/<int:pk>/', views.ItineraryDetailView.as_view()),
    path('api/itineraries/generate/', views.generate_itinerary),

    # Saved places
    path('api/saved-places/', views.SavedPlaceListCreateView.as_view()),

    # Budget
    path('api/budget/estimate/', views.budget_estimate),
]