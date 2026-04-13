import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { MapComponent } from '../../components/map/map';

@Component({
  selector: 'app-destination-detail',
  standalone: true,
  imports: [CommonModule, MapComponent],
  templateUrl: './destination-detail.html',
  styleUrl: './destination-detail.css'
})
export class DestinationDetail implements OnInit {
  destination: any = null;
  places: any[] = [];
  filteredPlaces: any[] = [];
  weather: any = null;

  activeFilters: string[] = [];
  priceFilter: string = '';
  indoorFilter: boolean | null = null;
  showTopRated: boolean = false;

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');

    this.api.getDestinations().subscribe(data => {
      this.destination = data.find((d: any) => d.id === Number(id));
      if (this.destination) {
        this.loadWeather(this.destination.id);
      }
      this.cdr.detectChanges();
    });

    this.loadPlaces(Number(id));
  }

  loadPlaces(destinationId: number, filters?: any) {
    this.api.getDestinationPlaces(destinationId, filters).subscribe({
      next: (data) => {
        this.places = data;
        this.filteredPlaces = [...data];
        this.cdr.detectChanges();
        this.loadPhotos();
      },
      error: (err) => {
        console.error('Ошибка загрузки мест:', err);
      }
    });
  }

  loadWeather(destinationId: number) {
    this.api.getWeather(destinationId).subscribe({
      next: (res) => this.weather = res,
      error: () => this.weather = null
    });
  }

  loadPhotos() {
    this.filteredPlaces.forEach((place: any, i) => {
      setTimeout(() => {
        this.api.getPlacePhoto(place.id).subscribe(res => {
          place.photoUrl = res.url;
          place.photoCredit = res.credit;
          this.cdr.detectChanges();
        });
      }, i * 100);
    });
  }

  savePlace(placeId: number) {
    this.api.savePlace(placeId).subscribe();
  }


  togglePriceFilter(level: string) {
    if (this.priceFilter === level) {
      this.priceFilter = '';
    } else {
      this.priceFilter = level;
    }
    this.applyFilters();
  }

  toggleIndoorFilter(isIndoor: boolean) {
    if (this.indoorFilter === isIndoor) {
      this.indoorFilter = null;
    } else {
      this.indoorFilter = isIndoor;
    }
    this.applyFilters();
  }

  toggleTopRated() {
    this.showTopRated = !this.showTopRated;
    this.applyFilters();
  }

  clearFilters() {
    this.priceFilter = '';
    this.indoorFilter = null;
    this.showTopRated = false;
    this.activeFilters = [];

    const id = this.route.snapshot.paramMap.get('id');
    this.loadPlaces(Number(id));
  }

  applyFilters() {
    const filters: any = {};
    this.activeFilters = [];

    if (this.priceFilter) {
      filters.price = this.priceFilter;
      if (this.priceFilter === 'budget') {
        this.activeFilters.push('💰 Бюджетные');
      } else if (this.priceFilter === 'premium') {
        this.activeFilters.push('💎 Премиум');
      }
    }

    if (this.indoorFilter !== null) {
      filters.indoor = this.indoorFilter;
      if (this.indoorFilter === true) {
        this.activeFilters.push('🏠 В помещении');
      } else {
        this.activeFilters.push('🌤️ На улице');
      }
    }

    if (this.showTopRated) {
      filters.top = '10';
      this.activeFilters.push('⭐ Топ-10');
    }

    const id = this.route.snapshot.paramMap.get('id');

    // ✅ ЗАПРОС К БЭКЕНДУ С ФИЛЬТРАМИ
    this.api.getDestinationPlaces(Number(id), filters).subscribe({
      next: (data) => {
        this.filteredPlaces = data;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Ошибка фильтрации:', err);
      }
    });
  }

  hasActiveFilters(): boolean {
    return this.activeFilters.length > 0;
  }
}
