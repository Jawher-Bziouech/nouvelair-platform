import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import {
  AssistantMessage,
  AssistantSession,
  QuestionResponse,
} from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class AssistantService {
  private readonly base = `${API_BASE_URL}/assistant`;
  private readonly sessionKey = 'nouvelair_assistant_session_id';

  constructor(private readonly http: HttpClient) {}

  ask(question: string, sessionId?: number | null): Observable<QuestionResponse> {
    return this.http.post<QuestionResponse>(`${this.base}/question`, {
      question,
      session_id: sessionId ?? null,
    });
  }

  listSessions(): Observable<AssistantSession[]> {
    return this.http.get<AssistantSession[]>(`${this.base}/sessions`);
  }

  getMessages(sessionId: number): Observable<AssistantMessage[]> {
    return this.http.get<AssistantMessage[]>(
      `${this.base}/sessions/${sessionId}/messages`,
    );
  }

  getStoredSessionId(): number | null {
    const raw = localStorage.getItem(this.sessionKey);
    if (!raw) {
      return null;
    }
    const id = Number(raw);
    return Number.isFinite(id) && id > 0 ? id : null;
  }

  storeSessionId(sessionId: number): void {
    localStorage.setItem(this.sessionKey, String(sessionId));
  }

  clearStoredSessionId(): void {
    localStorage.removeItem(this.sessionKey);
  }
}
