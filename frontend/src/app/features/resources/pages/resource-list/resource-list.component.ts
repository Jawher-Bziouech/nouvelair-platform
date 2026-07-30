import { Component, OnInit, inject } from '@angular/core';
import { AuthService } from '../../../../core/services/auth.service';
import { CategorieService } from '../../../../core/services/categorie.service';
import { RessourceService } from '../../../../core/services/ressource.service';
import { Categorie, Ressource } from '../../../../core/models/api.models';

@Component({
  selector: 'app-resource-list',
  standalone: false,
  templateUrl: './resource-list.component.html',
  styleUrl: './resource-list.component.scss',
})
export class ResourceListComponent implements OnInit {
  private readonly ressourceService = inject(RessourceService);
  private readonly categorieService = inject(CategorieService);
  private readonly auth = inject(AuthService);

  ressources: Ressource[] = [];
  categories: Categorie[] = [];
  q = '';
  categorieId: number | '' = '';
  type = '';
  error = '';
  loading = false;

  ngOnInit(): void {
    this.categorieService.list().subscribe({
      next: (cats: Categorie[]) => (this.categories = cats),
    });
    this.load();
  }

  get canManage(): boolean {
    return this.auth.hasRole('Administrateur', 'Manager');
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.ressourceService
      .list({
        q: this.q || undefined,
        type: this.type || undefined,
        categorie_id: this.categorieId === '' ? undefined : Number(this.categorieId),
      })
      .subscribe({
        next: (items: Ressource[]) => {
          this.ressources = items;
          this.loading = false;
        },
        error: () => {
          this.error = 'Impossible de charger les ressources.';
          this.loading = false;
        },
      });
  }

  download(item: Ressource): void {
    const token = this.auth.getToken();
    const url = this.ressourceService.downloadUrl(item.id);
    fetch(url, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error('download failed');
        }
        const blob = await res.blob();
        const objectUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = objectUrl;
        a.download = `${item.titre}.${item.type_fichier || 'bin'}`;
        a.click();
        URL.revokeObjectURL(objectUrl);
      })
      .catch(() => {
        this.error = 'Téléchargement impossible.';
      });
  }

  remove(item: Ressource): void {
    if (!confirm(`Supprimer "${item.titre}" ?`)) {
      return;
    }
    this.ressourceService.delete(item.id).subscribe({
      next: () => this.load(),
      error: () => (this.error = 'Suppression impossible.'),
    });
  }
}
