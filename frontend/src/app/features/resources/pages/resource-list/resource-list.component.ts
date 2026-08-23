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

  /** All resources (for folder counts + root search). */
  allRessources: Ressource[] = [];
  /** Resources shown in the current folder / search. */
  ressources: Ressource[] = [];
  categories: Categorie[] = [];
  q = '';
  type = '';
  /** null = root (folders view); number = open category folder. */
  currentFolderId: number | null = null;
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

  get isRoot(): boolean {
    return this.currentFolderId === null && !this.q.trim() && !this.type;
  }

  get currentFolder(): Categorie | null {
    if (this.currentFolderId === null) {
      return null;
    }
    return this.categories.find((c) => c.id === this.currentFolderId) ?? null;
  }

  get folderTitle(): string {
    if (this.q.trim() || this.type) {
      return 'Résultats de recherche';
    }
    return this.currentFolder?.nom ?? 'Bibliothèque';
  }

  countInFolder(categorieId: number): number {
    return this.allRessources.filter((r) => r.categorie_id === categorieId).length;
  }

  openFolder(categorieId: number | null): void {
    this.currentFolderId = categorieId;
    this.q = '';
    this.type = '';
    this.applyView();
  }

  load(): void {
    this.loading = true;
    this.error = '';
    this.ressourceService.list({}).subscribe({
      next: (items: Ressource[]) => {
        this.allRessources = items;
        this.applyView();
        this.loading = false;
      },
      error: () => {
        this.error = 'Impossible de charger les ressources.';
        this.loading = false;
      },
    });
  }

  search(): void {
    this.applyView();
  }

  clearSearch(): void {
    this.q = '';
    this.type = '';
    this.applyView();
  }

  private applyView(): void {
    let items = [...this.allRessources];
    const query = this.q.trim().toLowerCase();

    if (query) {
      items = items.filter((r) => r.titre.toLowerCase().includes(query));
    }
    if (this.type) {
      items = items.filter((r) => r.type === this.type);
    }
    if (!query && !this.type && this.currentFolderId !== null) {
      items = items.filter((r) => r.categorie_id === this.currentFolderId);
    }

    this.ressources = items;
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
