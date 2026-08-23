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

export interface ChartSlice {
  label: string;
  value: number;
  color: string;
  pct: number;
}

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

  private readonly palette = [
    '#0b2a4a',
    '#0b5cad',
    '#1a7bbf',
    '#c8102e',
    '#c47a12',
    '#0f7a62',
    '#5b6b7c',
    '#7c3aed',
  ];

  stats: DashboardStats | null = null;
  recentUsers: User[] = [];
  recentRessources: Ressource[] = [];
  categories: Categorie[] = [];
  byRole: ChartSlice[] = [];
  byType: ChartSlice[] = [];
  byCategory: ChartSlice[] = [];
  indexRing = '';
  indexedPct = 0;
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

        this.byRole = this.toSlices(
          this.countMap(users.map((u) => u.role?.nom || 'Sans rôle'))
        );
        this.byType = this.toSlices(this.countMap(ressources.map((r) => r.type || 'autre')));
        this.byCategory = this.toSlices(
          this.countMap(
            ressources.map((r) => r.categorie?.nom || 'Sans catégorie')
          )
        );

        const total = stats.ressources || 0;
        this.indexedPct =
          total === 0 ? 0 : Math.round((stats.ressources_indexees / total) * 100);
        this.indexRing = this.donutGradient([
          { label: 'Indexées', value: stats.ressources_indexees, color: '#0f7a62', pct: 0 },
          {
            label: 'Non indexées',
            value: Math.max(0, total - stats.ressources_indexees),
            color: '#e8ecf1',
            pct: 0,
          },
        ]);

        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Impossible de charger le dashboard.';
      },
    });
  }

  private countMap(labels: string[]): Record<string, number> {
    return labels.reduce<Record<string, number>>((acc, label) => {
      acc[label] = (acc[label] || 0) + 1;
      return acc;
    }, {});
  }

  private toSlices(map: Record<string, number>): ChartSlice[] {
    const entries = Object.entries(map).sort((a, b) => b[1] - a[1]);
    const total = entries.reduce((sum, [, v]) => sum + v, 0) || 1;
    return entries.map(([label, value], i) => ({
      label,
      value,
      color: this.palette[i % this.palette.length],
      pct: Math.round((value / total) * 100),
    }));
  }

  donutGradient(slices: ChartSlice[]): string {
    const total = slices.reduce((sum, s) => sum + s.value, 0);
    if (total === 0) {
      return 'conic-gradient(#e8ecf1 0deg 360deg)';
    }
    let angle = 0;
    const parts: string[] = [];
    for (const s of slices) {
      const next = angle + (s.value / total) * 360;
      parts.push(`${s.color} ${angle}deg ${next}deg`);
      angle = next;
    }
    return `conic-gradient(${parts.join(', ')})`;
  }

  maxBar(slices: ChartSlice[]): number {
    return Math.max(1, ...slices.map((s) => s.value));
  }
}
