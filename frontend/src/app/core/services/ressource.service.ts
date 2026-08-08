import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import { Ressource } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class RessourceService {
  private readonly base = `${API_BASE_URL}/ressources`;

  constructor(private readonly http: HttpClient) {}

  list(filters?: {
    categorie_id?: number;
    type?: string;
    q?: string;
  }): Observable<Ressource[]> {
    let params = new HttpParams();
    if (filters?.categorie_id != null) {
      params = params.set('categorie_id', filters.categorie_id);
    }
    if (filters?.type) {
      params = params.set('type', filters.type);
    }
    if (filters?.q) {
      params = params.set('q', filters.q);
    }
    return this.http.get<Ressource[]>(`${this.base}/`, { params });
  }

  get(id: number): Observable<Ressource> {
    return this.http.get<Ressource>(`${this.base}/${id}`);
  }

  upload(formData: FormData): Observable<Ressource> {
    return this.http.post<Ressource>(`${this.base}/upload`, formData);
  }

  create(payload: {
    titre: string;
    type: string;
    categorie_id: number;
    contenu?: string | null;
    type_fichier?: string | null;
    chemin_fichier?: string | null;
  }): Observable<Ressource> {
    return this.http.post<Ressource>(`${this.base}/`, payload);
  }

  update(
    id: number,
    payload: Partial<{
      titre: string;
      type: string;
      contenu: string | null;
      type_fichier: string | null;
      chemin_fichier: string | null;
      categorie_id: number;
      est_indexe: boolean;
    }>,
  ): Observable<Ressource> {
    return this.http.put<Ressource>(`${this.base}/${id}`, payload);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }

  reindex(id: number): Observable<Ressource> {
    return this.http.post<Ressource>(`${this.base}/${id}/reindex`, {});
  }

  downloadUrl(id: number): string {
    return `${this.base}/${id}/download`;
  }

  previewUrl(id: number): string {
    return `${this.base}/${id}/preview`;
  }
}
