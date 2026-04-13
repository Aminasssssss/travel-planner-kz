import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-city-events',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './city-events.html',
  styleUrls: ['./city-events.css']
})
export class CityEvents implements OnInit {
  cityId: number = 0;
  city: any = null;
  events: any[] = [];
  categories: string[] = [];
  selectedCategory: string = '';
  loading: boolean = false;
  error: string = '';

  categoryIcons: any = {
    'concert': '🎵', 'theatre': '🎭', 'masterclass': '🎨',
    'food': '🍽️', 'sport': '🏃', 'kids': '👶',
    'exhibition': '🖼️', 'party': '🎉'
  };

  categoryLabels: any = {
    'concert': 'Концерты', 'theatre': 'Театр', 'masterclass': 'Мастер-классы',
    'food': 'Гастро', 'sport': 'Спорт', 'kids': 'Детям',
    'exhibition': 'Выставки', 'party': 'Вечеринки'
  };

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.cityId = Number(this.route.snapshot.paramMap.get('id'));

    this.loading = true;
    this.cdr.detectChanges();

    this.api.getDestination(this.cityId).subscribe({
      next: (city) => {
        this.city = city;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Ошибка города:', err);
        this.error = 'Город не найден';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });

    this.api.getCityEvents(this.cityId).subscribe({
      next: (events) => {
        this.events = events;
        this.extractCategories();
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Ошибка событий:', err);
        this.error = 'События не найдены';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  extractCategories() {
    const cats = new Set<string>();
    this.events.forEach(event => {
      if (event.category) cats.add(event.category);
    });
    this.categories = Array.from(cats);
  }

  filterByCategory(category: string) {
    this.selectedCategory = category;
    this.loading = true;
    this.cdr.detectChanges();

    this.api.getCityEvents(this.cityId, category).subscribe({
      next: (data) => {
        this.events = data;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  clearFilter() {
    this.selectedCategory = '';
    this.loading = true;
    this.cdr.detectChanges();

    this.api.getCityEvents(this.cityId).subscribe({
      next: (events) => {
        this.events = events;
        this.extractCategories();
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  getCategoryIcon(cat: string): string {
    return this.categoryIcons[cat] || '📅';
  }

  getCategoryLabel(cat: string): string {
    return this.categoryLabels[cat] || cat;
  }

  formatDate(dateStr: string, timeStr?: string): string {
    const date = new Date(dateStr);
    const options: Intl.DateTimeFormatOptions = {
      day: 'numeric',
      month: 'long'
    };

    let result = date.toLocaleDateString('ru-RU', options);

    if (timeStr) {
      result += `, ${timeStr.slice(0, 5)}`;
    }

    return result;
  }

  get filteredEvents(): any[] {
    if (!this.selectedCategory) return this.events;
    return this.events.filter(e => e.category === this.selectedCategory);
  }
}
