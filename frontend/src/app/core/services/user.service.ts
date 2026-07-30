import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import { User } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class UserService {
  private readonly base = `${API_BASE_URL}/users`;

  constructor(private readonly http: HttpClient) {}

  list(): Observable<User[]> {
    return this.http.get<User[]>(`${this.base}/`);
  }

  create(payload: {
    nom: string;
    prenom: string;
    email: string;
    mot_de_passe: string;
    role_id: number;
  }): Observable<User> {
    return this.http.post<User>(`${this.base}/`, payload);
  }

  update(
    id: number,
    payload: Partial<{
      nom: string;
      prenom: string;
      email: string;
      mot_de_passe: string;
      role_id: number;
    }>,
  ): Observable<User> {
    return this.http.put<User>(`${this.base}/${id}`, payload);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
