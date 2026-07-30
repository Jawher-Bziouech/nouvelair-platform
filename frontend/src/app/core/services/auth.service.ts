import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { API_BASE_URL } from '../api.config';
import { TokenResponse, User } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly tokenKey = 'nouvelair_token';
  private readonly currentUserSubject = new BehaviorSubject<User | null>(null);
  readonly currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private readonly http: HttpClient,
    private readonly router: Router,
  ) {}

  login(email: string, password: string): Observable<TokenResponse> {
    const body = new URLSearchParams();
    body.set('username', email);
    body.set('password', password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
    });

    return this.http
      .post<TokenResponse>(`${API_BASE_URL}/auth/login`, body.toString(), {
        headers,
      })
      .pipe(
        tap((res) => {
          localStorage.setItem(this.tokenKey, res.access_token);
        }),
      );
  }

  loadMe(): Observable<User> {
    return this.http.get<User>(`${API_BASE_URL}/auth/me`).pipe(
      tap((user) => this.currentUserSubject.next(user)),
    );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    this.currentUserSubject.next(null);
    this.router.navigate(['/auth/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  get currentUser(): User | null {
    return this.currentUserSubject.value;
  }

  hasRole(...roles: string[]): boolean {
    const roleName = this.currentUser?.role?.nom;
    return !!roleName && roles.includes(roleName);
  }
}
