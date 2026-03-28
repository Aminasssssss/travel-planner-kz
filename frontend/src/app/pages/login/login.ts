import { Component, ChangeDetectorRef } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  username = '';
  password = '';
  error = '';
  loading = false;

  constructor(
    private api: ApiService,
    public router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  login() {
    this.loading = true;
    this.error = '';
    this.api.login(this.username, this.password).subscribe({
      next: (data: any) => {
        localStorage.setItem('access_token', data.access);
        this.router.navigate(['/']);
      },
      error: () => {
        this.error = 'Invalid username or password';
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }
}
