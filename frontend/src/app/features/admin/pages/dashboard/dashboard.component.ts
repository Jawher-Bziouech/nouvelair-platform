import { Component, OnInit, inject } from '@angular/core';
import { forkJoin } from 'rxjs';
import { DashboardService } from '../../../../core/services/dashboard.service';
import { UserService } from '../../../../core/services/user.service';
import { CategorieService } from '../../../../core/services/categorie.service';
import { RessourceService } from '../../../../core/services/ressource.service';
import {
  Categorie,
  DashboardStats,
  Ressource,
  User,
} from '../../../../core/models/api.models';

@Component({
  selector: 'app-dashboard',
  standalone: false,
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  private readonly dashboardService = inject(DashboardService);
  private readonly userService = inject(UserService);
  private readonly categorieService = inject(CategorieService);
  private readonly ressourceService = inject(RessourceService);

  stats: DashboardStats | null = null;
  recentUsers: User[] = [];
  recentRessources: Ressource[] = [];
  categories: Categorie[] = [];
  loading = true;
  error = '';

  ngOnInit(): void {
    forkJoin({
      stats: this.dashboardService.getStats(),
      users: this.userService.list(),
      categories: this.categorieService.list(),
      ressources: this.ressourceService.list(),
    }).subscribe({
      next: ({ stats, users, categories, ressources }) => {
        this.stats = stats;
        this.categories = categories;
        this.recentUsers = [...users]
          .sort((a, b) => (b.date_creation || '').localeCompare(a.date_creation || ''))
          .slice(0, 5);
        this.recentRessources = [...ressources]
          .sort((a, b) => (b.date_ajout || '').localeCompare(a.date_ajout || ''))
          .slice(0, 5);
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Impossible de charger le dashboard.';
      },
    });
  }
}
