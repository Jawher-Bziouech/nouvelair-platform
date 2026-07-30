import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import { Categorie } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class CategorieService {
  private readonly base = `${API_BASE_URL}/categories`;

  constructor(private readonly http: HttpClient) {}

  list(): Observable<Categorie[]> {
    return this.http.get<Categorie[]>(`${this.base}/`);
  }

  create(payload: {
    nom: string;
    description?: string | null;
  }): Observable<Categorie> {
    return this.http.post<Categorie>(`${this.base}/`, payload);
  }

  update(
    id: number,
    payload: Partial<{ nom: string; description: string | null }>,
  ): Observable<Categorie> {
    return this.http.put<Categorie>(`${this.base}/${id}`, payload);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
