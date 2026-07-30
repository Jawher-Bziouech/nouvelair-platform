import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import { Role } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class RoleService {
  private readonly base = `${API_BASE_URL}/roles`;

  constructor(private readonly http: HttpClient) {}

  list(): Observable<Role[]> {
    return this.http.get<Role[]>(`${this.base}/`);
  }

  create(nom: string): Observable<Role> {
    return this.http.post<Role>(`${this.base}/`, { nom });
  }

  update(id: number, nom: string): Observable<Role> {
    return this.http.put<Role>(`${this.base}/${id}`, { nom });
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
