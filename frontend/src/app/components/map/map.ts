import { Component, Input, AfterViewInit, Output, EventEmitter, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import * as L from 'leaflet';

// @ts-ignore
import 'leaflet.markercluster';
// @ts-ignore
import 'leaflet-arrowheads';
// @ts-ignore
import 'leaflet.heat';

declare module 'leaflet' {
  interface PolylineOptions {
    arrowheads?: any;
  }
}

@Component({
  selector: 'app-map',
  standalone: true,
  templateUrl: './map.html',
  styleUrls: ['./map.css']
})
export class MapComponent implements AfterViewInit, OnDestroy {
  @ViewChild('mapContainer', { static: true }) mapContainer!: ElementRef;

  @Input() places: any[] = [];
  @Input() center: [number, number] = [48.0196, 66.9237];
  @Input() zoom: number = 5;
  @Input() itineraryDays: any[] = [];
  @Output() placeClick = new EventEmitter<any>();

  private map: L.Map | null = null;
  private markerClusterGroup: any = null;
  private heatLayer: any = null;
  showHeatmap = false;

  private categoryColors: { [key: string]: string } = {
    'nature': '#10b981', 'history': '#8b5cf6', 'food': '#f59e0b',
    'active': '#ef4444', 'photo': '#ec4899', 'culture': '#6366f1',
    'nightlife': '#8b5cf6', 'shopping': '#f59e0b', 'family': '#14b8a6', 'lifestyle': '#a855f7'
  };

  private categoryIcons: { [key: string]: string } = {
    'nature': '🌲', 'history': '🏛️', 'food': '🍽️', 'active': '🏃',
    'photo': '📸', 'culture': '🎭', 'nightlife': '🎉', 'shopping': '🛍️',
    'family': '👨‍👩‍👧', 'lifestyle': '✨'
  };

  ngAfterViewInit() {
    setTimeout(() => {
      this.initMap();

      if (this.places?.length) {
        this.markerClusterGroup = (L as any).markerClusterGroup({
          showCoverageOnHover: false,
          maxClusterRadius: 50,
          iconCreateFunction: (cluster: any) => this.createClusterIcon(cluster)
        });
        this.addPlaces();
        this.map?.addLayer(this.markerClusterGroup);
      }

      if (this.itineraryDays?.length) {
        this.drawRoutes();
        this.fitBounds();
      }

      setTimeout(() => {
        this.map?.invalidateSize(true);
      }, 500);
    }, 200);
  }

  ngOnDestroy() {
    if (this.heatLayer) {
      this.map?.removeLayer(this.heatLayer);
      this.heatLayer = null;
    }
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
    this.markerClusterGroup = null;
  }

  private initMap() {
    this.map = L.map(this.mapContainer.nativeElement).setView(this.center, this.zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap'
    }).addTo(this.map);
  }

  private createClusterIcon(cluster: any): L.DivIcon {
    const count = cluster.getChildCount();
    let size = 40;
    let color = '#6366f1';
    if (count > 50) { size = 55; color = '#ec4899'; }
    else if (count > 20) { size = 48; color = '#8b5cf6'; }

    return L.divIcon({
      html: `<div style="background: ${color}; width: ${size}px; height: ${size}px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 16px; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">${count}</div>`,
      className: 'custom-cluster',
      iconSize: L.point(size, size)
    });
  }

  private createMarker(place: any): L.Marker {
    const category = place.category?.name || 'culture';
    const color = this.categoryColors[category] || '#6366f1';
    const icon = this.categoryIcons[category] || '📍';

    const customIcon = L.divIcon({
      html: `<div style="width: 36px; height: 36px; background: ${color}; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.3);"><div style="transform: rotate(45deg); color: white; font-size: 16px;">${icon}</div></div>`,
      className: 'custom-marker',
      iconSize: [36, 36],
      iconAnchor: [18, 36],
      popupAnchor: [0, -20]
    });

    const marker = L.marker([place.latitude, place.longitude], { icon: customIcon });
    marker.bindPopup(this.createPopup(place));
    marker.on('click', () => this.placeClick.emit(place));
    return marker;
  }

  private createPopup(place: any): string {
    return `
      <div style="min-width: 220px;">
        <h4 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700;">${place.name}</h4>
        <div style="display: flex; gap: 10px; margin-bottom: 8px; font-size: 13px;">
          <span style="color: #f59e0b;">⭐ ${place.rating || '—'}</span>
          <span style="color: #666;">💰 ${place.price_level || '—'}</span>
        </div>
        <p style="margin: 0 0 12px 0; font-size: 13px; color: #666; line-height: 1.4;">${place.description?.slice(0, 100) || ''}...</p>
        <button onclick="window.dispatchEvent(new CustomEvent('addToItinerary', {detail: ${place.id}}))" style="width: 100%; padding: 8px; background: #6366f1; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">➕ В маршрут</button>
      </div>
    `;
  }

  private addPlaces() {
    this.places.forEach(place => {
      if (place.latitude && place.longitude && this.markerClusterGroup) {
        this.markerClusterGroup.addLayer(this.createMarker(place));
      }
    });
  }

  private drawRoutes() {
    if (!this.map) return;
    const colors = ['#FF6B6B', '#4ECDC4', '#FFD93D', '#6C5CE7', '#A8E6CF'];

    this.itineraryDays.forEach((day: any, idx: number) => {
      const points = day.places
        .filter((p: any) => p.latitude && p.longitude)
        .map((p: any) => [p.latitude, p.longitude]);

      if (points.length > 1) {
        (L as any).polyline(points, {
          color: colors[idx % colors.length],
          weight: 4,
          opacity: 0.8,
          arrowheads: { frequency: 'endonly', size: '12px', fill: true }
        }).addTo(this.map!);
      }

      if (points.length > 0) {
        const midPoint = points[Math.floor(points.length / 2)];
        L.marker(midPoint as L.LatLngExpression, {
          icon: L.divIcon({
            html: `<div style="background: ${colors[idx % colors.length]}; color: white; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; white-space: nowrap; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">День ${idx + 1}</div>`,
            className: 'day-label',
            iconSize: [70, 28]
          })
        }).addTo(this.map!);
      }
    });
  }

  private fitBounds() {
    if (!this.map) return;
    const allPoints = this.itineraryDays.flatMap((d: any) => d.places.filter((p: any) => p.latitude && p.longitude));
    if (allPoints.length) {
      const bounds = L.latLngBounds(allPoints.map((p: any) => [p.latitude, p.longitude]));
      this.map.fitBounds(bounds, { padding: [50, 50] });
    }
  }

  toggleHeatmap() {
    this.showHeatmap = !this.showHeatmap;

    if (!this.map) return;

    try {
      if (this.showHeatmap) {
        if (this.markerClusterGroup) {
          this.map.removeLayer(this.markerClusterGroup);
        }

        const points = this.places
          .filter((p: any) => p.latitude && p.longitude)
          .map((p: any) => [p.latitude, p.longitude, (p.rating || 1) * 0.5]);

        this.heatLayer = (L as any).heatLayer(points, {
          radius: 25,
          blur: 15,
          maxZoom: 10,
          gradient: { 0.4: 'blue', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red' }
        }).addTo(this.map);
      } else {
        if (this.heatLayer) {
          this.map.removeLayer(this.heatLayer);
          this.heatLayer = null;
        }

        if (this.markerClusterGroup) {
          this.map.addLayer(this.markerClusterGroup);
        }
      }
    } catch (e) {
      console.warn('Heatmap failed, falling back to markers');
      this.showHeatmap = false;
      if (this.markerClusterGroup) {
        this.map.addLayer(this.markerClusterGroup);
      }
    }
  }
}
