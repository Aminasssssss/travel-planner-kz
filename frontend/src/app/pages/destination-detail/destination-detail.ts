import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-destination-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './destination-detail.html',
  styleUrl: './destination-detail.css'
})
export class DestinationDetail implements OnInit {
  destination: any = null;
  places: any[] = [];

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
      this.cdr.detectChanges();
    });
    this.api.getDestinationPlaces(Number(id)).subscribe(data => {
      this.places = [...data];
      this.cdr.detectChanges();
    });
  }

  savePlace(placeId: number) {
    this.api.savePlace(placeId).subscribe();
  }
}
