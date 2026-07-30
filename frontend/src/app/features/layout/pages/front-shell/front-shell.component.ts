import { Component, OnInit, inject } from '@angular/core';
import { AuthService } from '../../../../core/services/auth.service';
import { User } from '../../../../core/models/api.models';

@Component({
  selector: 'app-front-shell',
  standalone: false,
  templateUrl: './front-shell.component.html',
  styleUrl: './front-shell.component.scss',
})
export class FrontShellComponent implements OnInit {
  private readonly auth = inject(AuthService);
  user: User | null = null;

  ngOnInit(): void {
    if (!this.auth.currentUser && this.auth.isLoggedIn()) {
      this.auth.loadMe().subscribe({
        next: (user: User) => (this.user = user),
        error: () => this.auth.logout(),
      });
    }
    this.auth.currentUser$.subscribe((user: User | null) => (this.user = user));
  }

  get isAdmin(): boolean {
    return this.auth.hasRole('Administrateur');
  }

  get isManagerOrAdmin(): boolean {
    return this.auth.hasRole('Administrateur', 'Manager');
  }

  logout(): void {
    this.auth.logout();
  }
}
