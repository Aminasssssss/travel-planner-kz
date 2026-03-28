import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    });
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

  getDestinationPlaces(id: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/destinations/${id}/places/`);
  }

  getPopularPlaces(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/places/popular/`);
  }

  getMyItineraries(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/itineraries/`, { headers: this.getHeaders() });
  }

  generateItinerary(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/itineraries/generate/`, data, { headers: this.getHeaders() });
  }

  getItinerary(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/itineraries/${id}/`, { headers: this.getHeaders() });
  }

  updateItinerary(id: number, data: any): Observable<any> {
    return this.http.patch(`${this.baseUrl}/itineraries/${id}/`, data, { headers: this.getHeaders() });
  }

  deleteItinerary(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/itineraries/${id}/`, { headers: this.getHeaders() });
  }

  getBudgetEstimate(params: any): Observable<any> {
    return this.http.get(`${this.baseUrl}/budget/estimate/`, { params });
  }

  getSavedPlaces(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/saved-places/`, { headers: this.getHeaders() });
  }

  savePlace(placeId: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/saved-places/`, { place_id: placeId }, { headers: this.getHeaders() });
  }
}
