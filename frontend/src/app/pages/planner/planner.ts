import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-planner',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './planner.html',
  styleUrl: './planner.css'
})
export class Planner implements OnInit {
  destinations: any[] = [];
  selectedDestination = '';
  selectedDays = 3;
  selectedBudget = 'mid';
  selectedInterests: string[] = ['nature'];
  loading = false;
  error = '';

  interests = [
    { value: 'nature', label: '🏔️ Nature' },
    { value: 'history', label: '🏛️ History' },
    { value: 'food', label: '🍽️ Food' },
    { value: 'active', label: '🏃 Active' },
    { value: 'photo', label: '📸 Photo' },
  ];

  constructor(
    public router: Router,
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.api.getDestinations().subscribe(data => {
      this.destinations = [...data];
      if (data.length > 0) this.selectedDestination = data[0].id;
      this.cdr.detectChanges();
    });
  }

  toggleInterest(value: string) {
    if (this.selectedInterests.includes(value)) {
      this.selectedInterests = this.selectedInterests.filter(i => i !== value);
    } else {
      this.selectedInterests = [...this.selectedInterests, value];
    }
  }

  isSelected(value: string): boolean {
    return this.selectedInterests.includes(value);
  }

  generate() {
    if (!this.selectedDestination) return;
    if (this.selectedInterests.length === 0) {
      this.error = 'Please select at least one interest';
      return;
    }
    if (!localStorage.getItem('access_token')) {
      this.router.navigate(['/login']);
      return;
    }

    this.loading = true;
    this.error = '';

    const data = {
      destination_id: Number(this.selectedDestination),
      duration_days: this.selectedDays,
      budget_level: this.selectedBudget,
      interests: this.selectedInterests
    };

    this.api.generateItinerary(data).subscribe({
      next: (result: any) => {
        this.router.navigate(['/itinerary', result.id]);
      },
      error: () => {
        this.error = 'Failed to generate itinerary. Please try again.';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }
}
