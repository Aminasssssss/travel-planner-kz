import { Component } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs';
import { AiChatComponent } from './components/ai-chat/ai-chat';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, AiChatComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  showChat = true;

  constructor(private router: Router) {
    this.router.events.pipe(
      filter(e => e instanceof NavigationEnd)
    ).subscribe((e: any) => {
      this.showChat = !e.url.includes('/login') && !e.url.includes('/register');
    });
  }
}
