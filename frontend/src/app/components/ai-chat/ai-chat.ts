import { Component, Input, ViewChild, ElementRef, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-ai-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './ai-chat.html',
  styleUrl: './ai-chat.css'
})
export class AiChatComponent {
  @Input() destinationId?: number;
  @ViewChild('messagesContainer') messagesRef!: ElementRef;

  isOpen = false;
  question = '';
  messages: { id: number; text: string; isUser: boolean }[] = [];
  loading = false;
  private messageId = 0;

  constructor(
    private api: ApiService,
    private cdr: ChangeDetectorRef  // ← ДОБАВЬ ЭТО
  ) {}

  toggleChat() {
    this.isOpen = !this.isOpen;
    if (this.isOpen && this.messages.length === 0) {
      this.messages.push({
        id: ++this.messageId,
        text: '👋 Привет! Я AI-гид по Казахстану. Спросите про любое место!',
        isUser: false
      });
    }
    this.cdr.detectChanges();  // ← ДОБАВЬ
  }

  setQuestion(q: string) {
    this.question = q;
    this.ask();
  }

  scrollToBottom() {
    setTimeout(() => {
      if (this.messagesRef) {
        this.messagesRef.nativeElement.scrollTop = this.messagesRef.nativeElement.scrollHeight;
      }
    }, 50);
  }

  ask() {
    if (!this.question.trim() || this.loading) return;

    const q = this.question;
    this.messages.push({ id: ++this.messageId, text: q, isUser: true });
    this.question = '';
    this.loading = true;
    this.cdr.detectChanges();  // ← ДОБАВЬ
    this.scrollToBottom();

    this.api.askAI(q, this.destinationId).subscribe({
      next: (res) => {
        this.messages.push({ id: ++this.messageId, text: res.answer, isUser: false });
        this.loading = false;
        this.cdr.detectChanges();  // ← ДОБАВЬ
        this.scrollToBottom();
      },
      error: (err) => {
        console.error('AI Chat error:', err);
        this.messages.push({ id: ++this.messageId, text: 'Извините, ошибка.', isUser: false });
        this.loading = false;
        this.cdr.detectChanges();  // ← ДОБАВЬ
        this.scrollToBottom();
      }
    });
  }
}
