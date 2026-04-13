import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-itinerary-analysis',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './itinerary-analysis.html',
  styleUrls: ['./itinerary-analysis.css']
})
export class ItineraryAnalysis implements OnInit {
  itineraryId: number = 0;
  itinerary: any = null;

  tspResult: any = null;
  tspLoading = false;

  burnout: any = null;
  stats: any = null;

  loading = true;
  error = '';
  successMessage = '';
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.itineraryId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadData();
  }

  private loadData() {
    this.loading = true;

    this.api.getItinerary(this.itineraryId).subscribe({
      next: (data) => {
        this.itinerary = data;
        this.loadStats();
        this.loadBurnout();
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Маршрут не найден';
        this.loading = false;
      }
    });
  }

  loadStats() {
    this.api.getItineraryStats(this.itineraryId).subscribe({
      next: (data) => {
        this.stats = data;
        this.cdr.detectChanges();
      }
    });
  }

  loadBurnout() {
    this.api.getBurnoutAnalysis(this.itineraryId).subscribe({
      next: (data) => {
        this.burnout = data;
        this.cdr.detectChanges();
      }
    });
  }

  runOptimization() {
    this.tspLoading = true;
    this.tspResult = null;
    this.errorMessage = '';

    this.api.optimizeItinerary(this.itineraryId).subscribe({
      next: (data) => {
        this.tspResult = data;
        this.tspLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.errorMessage = '❌ Ошибка оптимизации';
        this.tspLoading = false;
        setTimeout(() => this.errorMessage = '', 3000);
        this.cdr.detectChanges();
      }
    });
  }

  applyOptimization() {
    if (!this.tspResult) return;

    const optimizedOrder = this.tspResult.days.map((day: any) => ({
      day: day.day,
      places: day.optimized_order
    }));

    this.api.applyOptimization(this.itineraryId, optimizedOrder).subscribe({
      next: () => {
        this.tspResult = null;
        this.loading = true;

        this.api.getItinerary(this.itineraryId).subscribe({
          next: (data) => {
            this.itinerary = data;

            this.api.getItineraryStats(this.itineraryId).subscribe({
              next: (statsData) => {
                this.stats = statsData;

                this.api.getBurnoutAnalysis(this.itineraryId).subscribe({
                  next: (burnoutData) => {
                    this.burnout = burnoutData;
                    this.loading = false;
                    this.successMessage = '✅ Оптимизация применена!';
                    setTimeout(() => this.successMessage = '', 3000);
                    this.cdr.detectChanges();
                  },
                  error: () => {
                    this.loading = false;
                    this.cdr.detectChanges();
                  }
                });
              },
              error: () => {
                this.loading = false;
                this.cdr.detectChanges();
              }
            });
          },
          error: () => {
            this.loading = false;
            this.errorMessage = '❌ Ошибка при обновлении';
            setTimeout(() => this.errorMessage = '', 3000);
            this.cdr.detectChanges();
          }
        });
      },
      error: () => {
        this.errorMessage = '❌ Ошибка при применении оптимизации';
        setTimeout(() => this.errorMessage = '', 3000);
        this.cdr.detectChanges();
      }
    });
  }

  getCategoryIcons(categories: any): string {
    const icons: any = {
      'nature': '🏔️', 'history': '🏛️', 'food': '🍽️', 'active': '🏃',
      'photo': '📸', 'culture': '🎭', 'nightlife': '🎉', 'shopping': '🛍️',
      'family': '👨‍👩‍👧', 'lifestyle': '✨'
    };

    return Object.entries(categories)
      .map(([cat, count]) => `${icons[cat] || '📍'} ${count}`)
      .join(' | ');
  }

  getBurnoutIcon(level: string): string {
    switch (level) {
      case 'optimal': return '🟢';
      case 'medium': return '🟡';
      case 'overload': return '🔴';
      default: return '⚪';
    }
  }
}
