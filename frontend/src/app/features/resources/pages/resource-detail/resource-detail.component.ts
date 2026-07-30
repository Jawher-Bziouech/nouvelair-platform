import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../../../core/services/auth.service';
import { CategorieService } from '../../../../core/services/categorie.service';
import { RessourceService } from '../../../../core/services/ressource.service';
import { Categorie, Ressource } from '../../../../core/models/api.models';

type PreviewKind = 'pdf' | 'text' | 'unsupported' | 'none';

@Component({
  selector: 'app-resource-detail',
  standalone: false,
  templateUrl: './resource-detail.component.html',
  styleUrl: './resource-detail.component.scss',
})
export class ResourceDetailComponent implements OnInit, OnDestroy {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);
  private readonly sanitizer = inject(DomSanitizer);
  private readonly ressourceService = inject(RessourceService);
  private readonly categorieService = inject(CategorieService);
  private readonly auth = inject(AuthService);

  ressource: Ressource | null = null;
  categories: Categorie[] = [];
  error = '';
  success = '';
  loading = true;
  saving = false;

  previewKind: PreviewKind = 'none';
  previewUrl: SafeResourceUrl | null = null;
  private objectUrl: string | null = null;
  previewText = '';
  previewLoading = false;
  previewError = '';

  form = this.fb.group({
    titre: ['', Validators.required],
    type: ['document', Validators.required],
    categorie_id: [null as number | null, Validators.required],
    contenu: [''],
  });

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!id) {
      this.error = 'Ressource invalide.';
      this.loading = false;
      return;
    }

    this.categorieService.list().subscribe({
      next: (cats: Categorie[]) => (this.categories = cats),
    });

    this.ressourceService.get(id).subscribe({
      next: (ressource: Ressource) => {
        this.ressource = ressource;
        this.form.setValue({
          titre: ressource.titre,
          type: ressource.type,
          categorie_id: ressource.categorie_id,
          contenu: ressource.contenu || '',
        });
        this.loading = false;
        this.loadPreview(ressource);
      },
      error: () => {
        this.error = 'Ressource introuvable.';
        this.loading = false;
      },
    });
  }

  ngOnDestroy(): void {
    this.clearPreviewUrl();
  }

  get canEdit(): boolean {
    if (!this.ressource) {
      return false;
    }
    if (this.auth.hasRole('Administrateur')) {
      return true;
    }
    return (
      this.auth.hasRole('Manager') &&
      this.auth.currentUser?.id === this.ressource.auteur_id
    );
  }

  private fileKind(ext: string | null | undefined): PreviewKind {
    const value = (ext || '').toLowerCase();
    if (!value) {
      return 'none';
    }
    if (value === 'pdf') {
      return 'pdf';
    }
    if (value === 'txt' || value === 'md') {
      return 'text';
    }
    return 'unsupported';
  }

  private clearPreviewUrl(): void {
    if (this.objectUrl) {
      URL.revokeObjectURL(this.objectUrl);
      this.objectUrl = null;
    }
    this.previewUrl = null;
  }

  private loadPreview(ressource: Ressource): void {
    this.clearPreviewUrl();
    this.previewText = '';
    this.previewError = '';

    if (!ressource.chemin_fichier) {
      this.previewKind = 'none';
      return;
    }

    this.previewKind = this.fileKind(ressource.type_fichier);
    if (this.previewKind === 'unsupported') {
      return;
    }

    this.previewLoading = true;
    const token = this.auth.getToken();
    const url = this.ressourceService.previewUrl(ressource.id);

    fetch(url, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error('preview failed');
        }
        if (this.previewKind === 'text') {
          this.previewText = await res.text();
        } else {
          const blob = await res.blob();
          this.objectUrl = URL.createObjectURL(blob);
          this.previewUrl = this.sanitizer.bypassSecurityTrustResourceUrl(this.objectUrl);
        }
        this.previewLoading = false;
      })
      .catch(() => {
        this.previewLoading = false;
        this.previewError = "Impossible d'afficher l'aperçu.";
      });
  }

  save(): void {
    if (!this.ressource || this.form.invalid || !this.canEdit) {
      this.form.markAllAsTouched();
      return;
    }

    const value = this.form.getRawValue();
    this.saving = true;
    this.error = '';
    this.success = '';

    this.ressourceService
      .update(this.ressource.id, {
        titre: value.titre!,
        type: value.type!,
        categorie_id: value.categorie_id!,
        contenu: (value.contenu || '').trim() || null,
      })
      .subscribe({
        next: (updated: Ressource) => {
          this.ressource = updated;
          this.saving = false;
          this.success = 'Modifications enregistrées.';
        },
        error: () => {
          this.saving = false;
          this.error = 'Mise à jour impossible.';
        },
      });
  }

  download(): void {
    if (!this.ressource?.chemin_fichier) {
      return;
    }
    const token = this.auth.getToken();
    const url = this.ressourceService.downloadUrl(this.ressource.id);
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
        a.download = `${this.ressource!.titre}.${this.ressource!.type_fichier || 'bin'}`;
        a.click();
        URL.revokeObjectURL(objectUrl);
      })
      .catch(() => {
        this.error = 'Téléchargement impossible.';
      });
  }

  remove(): void {
    if (!this.ressource || !this.canEdit) {
      return;
    }
    if (!confirm(`Supprimer "${this.ressource.titre}" ?`)) {
      return;
    }
    this.ressourceService.delete(this.ressource.id).subscribe({
      next: () => this.router.navigate(['/home']),
      error: () => (this.error = 'Suppression impossible.'),
    });
  }
}
