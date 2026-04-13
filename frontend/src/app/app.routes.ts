import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/home/home').then(m => m.Home)
  },

  {
    path: 'login',
    loadComponent: () => import('./pages/login/login').then(m => m.Login)
  },
  {
    path: 'register',
    loadComponent: () => import('./pages/register/register').then(m => m.Register)
  },
  {
    path: 'destinations',
    loadComponent: () => import('./pages/destinations/destinations').then(m => m.Destinations)
  },
  {
    path: 'destinations/:id',
    loadComponent: () => import('./pages/destination-detail/destination-detail').then(m => m.DestinationDetail)
  },
  {
    path: 'planner',
    loadComponent: () => import('./pages/planner/planner').then(m => m.Planner)
  },
  {
    path: 'shared/itinerary/:token',
    loadComponent: () => import('./pages/shared-itinerary/shared-itinerary').then(m => m.SharedItinerary)
  },
  {
    path: 'itinerary/:id',
    loadComponent: () => import('./pages/itinerary-detail/itinerary-detail').then(m => m.ItineraryDetail)
  },

  {
    path: 'city/:id/events',
    loadComponent: () => import('./pages/city-events/city-events').then(m => m.CityEvents)
  },

  {
    path: 'itinerary/:id/analysis',
    loadComponent: () => import('./pages/itinerary-analysis/itinerary-analysis').then(m => m.ItineraryAnalysis)
  },
  {
    path: 'my-trips',
    loadComponent: () => import('./pages/my-trips/my-trips').then(m => m.MyTrips)
  },
  {
    path: '**',
    redirectTo: ''
  },


];
