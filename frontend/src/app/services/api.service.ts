import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { HttpParams } from '@angular/common/http';


@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  shareItinerary(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/itineraries/${id}/share/`, {});
  }

  unshareItinerary(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/itineraries/${id}/unshare/`, {});
  }
  getSharedItinerary(token: string): Observable<any> {
    const url = `${this.baseUrl}/shared/${token}/`;
    console.log('Запрос к:', url);
    return this.http.get(url);
  }
  login(username: string, password: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/login/`, { username, password });
  }

  register(username: string, email: string, password: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/register/`, { username, email, password });
  }

  getDestinations(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/destinations/`);
  }



  getPopularPlaces(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/places/popular/`);
  }

  getMyItineraries(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/itineraries/`);
  }

  generateItinerary(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/itineraries/generate/`, data);
  }

  getItinerary(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/itineraries/${id}/`);
  }

  updateItinerary(id: number, data: any): Observable<any> {
    return this.http.patch(`${this.baseUrl}/itineraries/${id}/`, data);
  }

  deleteItinerary(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/itineraries/${id}/`);
  }

  getBudgetEstimate(params: any): Observable<any> {
    return this.http.get(`${this.baseUrl}/budget/estimate/`, { params });
  }

  getSavedPlaces(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/saved-places/`);
  }

  savePlace(placeId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/saved-places/`, { place_id: placeId });
  }
  getWeather(destinationId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/destinations/${destinationId}/weather/`);
  }
  getRecommendedPlaces(destinationId: number, placeId?: number): Observable<any[]> {
    const params: any = { destination_id: destinationId };
    if (placeId) params.place_id = placeId;
    return this.http.get<any[]>(`${this.baseUrl}/places/recommend/`, { params });
  }
  getPlacePhoto(placeId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/places/${placeId}/photo/`);
  }
  getClusteredPlaces(destinationId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/destinations/${destinationId}/clusters/`);
  }
  askAI(question: string, destinationId?: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/ai/chat/`, {
      question,
      destination_id: destinationId
    });

  }

  optimizeItinerary(id: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/itineraries/${id}/optimize/`, {});
  }

  applyOptimization(id: number, optimizedOrder: any[]): Observable<any> {
    return this.http.post(`${this.baseUrl}/itineraries/${id}/apply-optimization/`, {
      optimized_order: optimizedOrder
    });
  }

  getBurnoutAnalysis(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/itineraries/${id}/burnout/`);
  }

  getItineraryStats(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/itineraries/${id}/stats/`);
  }
  getDestination(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/destinations/${id}/`);
  }

  getCityEvents(cityId: number, category?: string): Observable<any> {
    let url = `${this.baseUrl}/cities/${cityId}/events/`;
    if (category) {
      url += `?category=${category}`;
    }
    return this.http.get(url);
  }
  addPlaceToDay(itineraryId: number, dayNumber: number, placeId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/itineraries/${itineraryId}/add-place/`, {
      day_number: dayNumber, place_id: placeId
    });
  }

  removePlaceFromDay(itineraryId: number, dayNumber: number, placeId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/itineraries/${itineraryId}/remove-place/`, {
      body: { day_number: dayNumber, place_id: placeId }
    });
  }

  movePlace(itineraryId: number, fromDay: number, toDay: number, placeId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/itineraries/${itineraryId}/move-place/`, {
      from_day: fromDay, to_day: toDay, place_id: placeId
    });
  }

  getPlaces(destinationId: number, params?: any): Observable<any> {
    let url = `${this.baseUrl}/destinations/${destinationId}/places/`;
    if (params?.search) url += `?search=${params.search}`;
    return this.http.get(url);
  }

  getEventCategories(cityId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/events/categories/?city_id=${cityId}`);
  }
  getDestinationPlaces(id: number, filters?: any): Observable<any[]> {
    let params = new HttpParams();

    if (filters?.price) {
      params = params.set('price', filters.price);
    }
    if (filters?.indoor !== undefined) {
      params = params.set('indoor', filters.indoor.toString());
    }
    if (filters?.top) {
      params = params.set('top', filters.top);
    }

    return this.http.get<any[]>(`${this.baseUrl}/destinations/${id}/places/`, { params });
  }
}
