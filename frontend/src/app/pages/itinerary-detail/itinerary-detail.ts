import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-itinerary-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './itinerary-detail.html',
  styleUrl: './itinerary-detail.css'
})
export class ItineraryDetail implements OnInit {
  itinerary: any = null;

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    this.api.getItinerary(Number(id)).subscribe(data => {
      this.itinerary = data;
      this.cdr.detectChanges();
    });
  }

  delete() {
    if (!this.itinerary) return;
    this.api.deleteItinerary(this.itinerary.id).subscribe(() => {
      this.router.navigate(['/my-trips']);
    });
  }
}
