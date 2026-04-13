import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';
import { MapComponent } from '../../components/map/map';

@Component({
  selector: 'app-itinerary-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, MapComponent],
  templateUrl: './itinerary-detail.html',
  styleUrl: './itinerary-detail.css'
})
export class ItineraryDetail implements OnInit {
  itinerary: any = null;
  shareUrl: string = '';
  loading: boolean = false;
  error: string = '';

  // Модалка добавления места
  showAddModal = false;
  targetDay: number = 0;
  searchQuery = '';
  searchResults: any[] = [];
  searchLoading = false;

  successMessage = '';

  constructor(
    private route: ActivatedRoute,
    public router: Router,
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    this.loadItinerary(Number(id));
  }

  loadItinerary(id: number) {
    this.api.getItinerary(id).subscribe(data => {
      this.itinerary = data;
      if (this.itinerary.is_public && this.itinerary.share_token) {
        this.shareUrl = window.location.origin + '/shared/itinerary/' + this.itinerary.share_token;
      }
      this.cdr.detectChanges();
    });
  }

  getAllPlaces() {
    if (!this.itinerary?.days) return [];
    return this.itinerary.days.flatMap((d: any) => d.places);
  }

  delete() {
    if (!this.itinerary) return;
    this.api.deleteItinerary(this.itinerary.id).subscribe(() => {
      this.router.navigate(['/my-trips']);
    });
  }

  shareItinerary() {
    this.loading = true;
    this.error = '';
    this.api.shareItinerary(this.itinerary.id).subscribe({
      next: (res: any) => {
        this.shareUrl = window.location.origin + res.share_url;
        this.itinerary.is_public = true;
        this.loading = false;
      },
      error: () => {
        this.error = 'Не удалось поделиться';
        this.loading = false;
      }
    });
  }

  unshareItinerary() {
    this.api.unshareItinerary(this.itinerary.id).subscribe({
      next: () => {
        this.itinerary.is_public = false;
        this.shareUrl = '';
      },
      error: () => {
        this.error = 'Не удалось закрыть доступ';
      }
    });
  }

  copyLink() {
    navigator.clipboard.writeText(this.shareUrl);
    alert('Ссылка скопирована!');
  }

  removePlace(dayNumber: number, placeId: number) {
    this.api.removePlaceFromDay(this.itinerary.id, dayNumber, placeId).subscribe({
      next: () => {
        this.showSuccess('Место удалено');
        this.loadItinerary(this.itinerary.id);
      },
      error: () => this.error = 'Ошибка при удалении'
    });
  }

  movePlace(fromDay: number, placeId: number, event: any) {
    const toDay = Number(event.target.value);
    if (!toDay) return;

    this.api.movePlace(this.itinerary.id, fromDay, toDay, placeId).subscribe({
      next: () => {
        this.showSuccess(`Место перемещено в День ${toDay}`);
        this.loadItinerary(this.itinerary.id);
        event.target.value = '';
      },
      error: () => this.error = 'Ошибка при перемещении'
    });
  }

  openAddPlaceModal(dayNumber: number) {
    this.targetDay = dayNumber;
    this.showAddModal = true;
    this.searchQuery = '';
    this.searchResults = [];
  }

  closeModal() {
    this.showAddModal = false;
    this.searchQuery = '';
    this.searchResults = [];
  }

  searchPlaces() {
    if (!this.searchQuery.trim()) return;
    this.searchLoading = true;

    const destId = this.itinerary.destination.id;
    this.api.getPlaces(destId, { search: this.searchQuery }).subscribe({
      next: (data: any) => {
        this.searchResults = data;
        this.searchLoading = false;
        this.cdr.detectChanges();
      },
      error: () => this.searchLoading = false
    });
  }

  addPlace(placeId: number) {
    this.api.addPlaceToDay(this.itinerary.id, this.targetDay, placeId).subscribe({
      next: () => {
        this.showSuccess('Место добавлено!');
        this.closeModal();
        this.loadItinerary(this.itinerary.id);
      },
      error: () => this.error = 'Ошибка при добавлении'
    });
  }

  showSuccess(msg: string) {
    this.successMessage = msg;
    setTimeout(() => this.successMessage = '', 3000);
  }
}
