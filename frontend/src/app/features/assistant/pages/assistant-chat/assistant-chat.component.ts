import { Component, ElementRef, OnInit, ViewChild, inject } from '@angular/core';
import { AssistantService } from '../../../../core/services/assistant.service';
import { AssistantMessage, Citation } from '../../../../core/models/api.models';

@Component({
  selector: 'app-assistant-chat',
  standalone: false,
  templateUrl: './assistant-chat.component.html',
  styleUrl: './assistant-chat.component.scss',
})
export class AssistantChatComponent implements OnInit {
  private readonly assistant = inject(AssistantService);

  @ViewChild('thread') threadRef?: ElementRef<HTMLElement>;

  question = '';
  sessionId: number | null = null;
  messages: AssistantMessage[] = [];
  loading = false;
  restoring = false;
  error = '';
  mode: string | null = null;

  ngOnInit(): void {
    const stored = this.assistant.getStoredSessionId();
    if (!stored) {
      return;
    }

    this.restoring = true;
    this.sessionId = stored;
    this.assistant.getMessages(stored).subscribe({
      next: (msgs) => {
        this.messages = msgs;
        this.restoring = false;
        this.scrollBottom();
      },
      error: () => {
        // Session gone (reseed / other user) → start clean
        this.assistant.clearStoredSessionId();
        this.sessionId = null;
        this.messages = [];
        this.restoring = false;
      },
    });
  }

  send(): void {
    const q = this.question.trim();
    if (!q || this.loading || this.restoring) {
      return;
    }

    this.error = '';
    this.loading = true;
    this.question = '';

    this.messages = [
      ...this.messages,
      {
        id: -Date.now(),
        session_id: this.sessionId || 0,
        texte: q,
        role: 'user',
        citations: [],
      },
    ];
    this.scrollBottom();

    this.assistant.ask(q, this.sessionId).subscribe({
      next: (res) => {
        this.sessionId = res.session_id;
        this.assistant.storeSessionId(res.session_id);
        this.mode = res.mode;
        const prior = this.messages.filter((m) => m.id > 0);
        this.messages = [...prior, res.question, res.answer];
        this.loading = false;
        this.scrollBottom();
      },
      error: (err) => {
        this.loading = false;
        const detail = err?.error?.detail;
        this.error =
          (typeof detail === 'string' ? detail : null) ||
          (err?.status === 0
            ? 'Impossible de contacter l’assistant. Vérifiez que l’API tourne.'
            : `Erreur assistant (${err?.status || '?'}). Réessayez.`);
      },
    });
  }

  newChat(): void {
    this.assistant.clearStoredSessionId();
    this.sessionId = null;
    this.messages = [];
    this.error = '';
    this.mode = null;
    this.question = '';
  }

  citationTitle(c: Citation): string {
    return c.titre_ressource || `Ressource #${c.ressource_id}`;
  }

  get modeLabel(): string {
    switch (this.mode) {
      case 'gemini':
        return 'Gemini (RAG, gratuit)';
      case 'groq':
        return 'Groq (RAG, gratuit)';
      case 'openai':
        return 'OpenAI (RAG)';
      case 'local':
        return 'local (extraits indexés)';
      default:
        return this.mode || '';
    }
  }

  private scrollBottom(): void {
    setTimeout(() => {
      const el = this.threadRef?.nativeElement;
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
    });
  }
}
