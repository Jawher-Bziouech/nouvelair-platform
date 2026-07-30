import { Component, OnInit, inject } from '@angular/core';
import { AuthService } from '../../../../core/services/auth.service';
import { User } from '../../../../core/models/api.models';

@Component({
  selector: 'app-admin-shell',
  standalone: false,
  templateUrl: './admin-shell.component.html',
  styleUrls: ['./admin-shell.component.scss'],
})
export class AdminShellComponent implements OnInit {
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

  logout(): void {
    this.auth.logout();
  }
}
