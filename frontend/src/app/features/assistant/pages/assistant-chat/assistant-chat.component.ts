import { Component, ElementRef, OnInit, ViewChild, inject } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
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
  private readonly sanitizer = inject(DomSanitizer);

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

  scoreLabel(score: number | null | undefined): string {
    if (score == null || Number.isNaN(Number(score))) {
      return '';
    }
    return `Pertinence ${Math.round(Number(score) * 100)} %`;
  }

  formatMessage(text: string): SafeHtml {
    return this.sanitizer.bypassSecurityTrustHtml(this.toReadableHtml(text));
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
        return 'local (réponse reformulée)';
      case 'local-fallback':
        return 'secours (Gemini indisponible)';
      case 'greeting':
        return '';
      default:
        return this.mode || '';
    }
  }

  private toReadableHtml(raw: string): string {
    let text = (raw || '').replace(/\r\n/g, '\n').trim();
    if (!text) {
      return '';
    }

    // Break jammed inline lists into real lines
    text = text.replace(/([^\n])\s+(\d{1,2})\.\s+/g, '$1\n$2. ');
    text = text.replace(/([^\n])\s+([•\-–])\s+/g, '$1\n- ');
    text = text.replace(/\s*—\s*/g, ' — ');

    const escape = (s: string) =>
      s
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    const inline = (s: string) =>
      escape(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    const blocks = text.split(/\n{2,}/);
    const htmlBlocks: string[] = [];

    for (const block of blocks) {
      const lines = block.split('\n').map((l) => l.trim()).filter(Boolean);
      if (!lines.length) {
        continue;
      }

      const allNumbered = lines.every((l) => /^\d+\.\s+/.test(l));
      const allBullets = lines.every((l) => /^[-•–]\s+/.test(l));

      if (allNumbered) {
        htmlBlocks.push(
          `<ol>${lines
            .map((l) => `<li>${inline(l.replace(/^\d+\.\s+/, ''))}</li>`)
            .join('')}</ol>`
        );
      } else if (allBullets) {
        htmlBlocks.push(
          `<ul>${lines
            .map((l) => `<li>${inline(l.replace(/^[-•–]\s+/, ''))}</li>`)
            .join('')}</ul>`
        );
      } else {
        const parts: string[] = [];
        let listBuf: { type: 'ol' | 'ul'; items: string[] } | null = null;

        const flushList = () => {
          if (!listBuf) {
            return;
          }
          const tag = listBuf.type;
          parts.push(
            `<${tag}>${listBuf.items.map((i) => `<li>${i}</li>`).join('')}</${tag}>`
          );
          listBuf = null;
        };

        for (const line of lines) {
          const numbered = line.match(/^(\d+)\.\s+(.*)$/);
          const bullet = line.match(/^[-•–]\s+(.*)$/);
          if (numbered) {
            if (!listBuf || listBuf.type !== 'ol') {
              flushList();
              listBuf = { type: 'ol', items: [] };
            }
            listBuf.items.push(inline(numbered[2]));
          } else if (bullet) {
            if (!listBuf || listBuf.type !== 'ul') {
              flushList();
              listBuf = { type: 'ul', items: [] };
            }
            listBuf.items.push(inline(bullet[1]));
          } else {
            flushList();
            parts.push(`<p>${inline(line)}</p>`);
          }
        }
        flushList();
        htmlBlocks.push(parts.join(''));
      }
    }

    return htmlBlocks.join('');
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
