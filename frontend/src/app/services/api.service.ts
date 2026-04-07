import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/login/`, { username, password });
  }

  register(username: string, email: string, password: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/auth/register/`, { username, email, password });
  }

  getDestinations(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/destinations/`);
  }

  getDestinationPlaces(id: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/destinations/${id}/places/`);
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
  getRecommendedPlaces(destinationId: number, placeId?: number): Observable<any[]> {
    const params: any = { destination_id: destinationId };
    if (placeId) params.place_id = placeId;
    return this.http.get<any[]>(`${this.baseUrl}/places/recommend/`, { params });
  }
}
