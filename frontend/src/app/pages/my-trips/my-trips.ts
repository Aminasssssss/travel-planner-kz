import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-my-trips',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './my-trips.html',
  styleUrl: './my-trips.css'
})
export class MyTrips implements OnInit {
  itineraries: any[] = [];

  constructor(
    public router: Router,
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    if (!localStorage.getItem('access_token')) {
      this.router.navigate(['/login']);
      return;
    }
    this.api.getMyItineraries().subscribe(data => {
      this.itineraries = [...data];
      this.cdr.detectChanges();
    });
  }

  delete(id: number) {
    this.api.deleteItinerary(id).subscribe(() => {
      this.itineraries = this.itineraries.filter(i => i.id !== id);
      this.cdr.detectChanges();
    });
  }
}
