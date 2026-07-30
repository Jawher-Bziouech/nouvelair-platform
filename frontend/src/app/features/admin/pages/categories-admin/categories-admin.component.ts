import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { CategorieService } from '../../../../core/services/categorie.service';
import { Categorie } from '../../../../core/models/api.models';

@Component({
  selector: 'app-categories-admin',
  standalone: false,
  templateUrl: './categories-admin.component.html',
  styleUrl: './categories-admin.component.scss',
})
export class CategoriesAdminComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly categorieService = inject(CategorieService);

  categories: Categorie[] = [];
  error = '';
  editingId: number | null = null;

  form = this.fb.group({
    nom: ['', Validators.required],
    description: [''],
  });

  ngOnInit(): void {
    this.load();
  }

  get isEditing(): boolean {
    return this.editingId !== null;
  }

  load(): void {
    this.categorieService.list().subscribe({
      next: (categories: Categorie[]) => (this.categories = categories),
      error: () => (this.error = 'Impossible de charger les catégories.'),
    });
  }

  startCreate(): void {
    this.editingId = null;
    this.error = '';
    this.form.reset({ nom: '', description: '' });
  }

  startEdit(cat: Categorie): void {
    this.editingId = cat.id;
    this.error = '';
    this.form.setValue({
      nom: cat.nom,
      description: cat.description || '',
    });
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    const payload = {
      nom: value.nom!,
      description: value.description || null,
    };

    if (this.editingId === null) {
      this.categorieService.create(payload).subscribe({
        next: () => {
          this.startCreate();
          this.load();
        },
        error: () => (this.error = 'Création impossible.'),
      });
      return;
    }

    this.categorieService.update(this.editingId, payload).subscribe({
      next: () => {
        this.startCreate();
        this.load();
      },
      error: () => (this.error = 'Mise à jour impossible.'),
    });
  }

  remove(cat: Categorie): void {
    if (!confirm(`Supprimer ${cat.nom} ?`)) {
      return;
    }
    this.categorieService.delete(cat.id).subscribe({
      next: () => {
        if (this.editingId === cat.id) {
          this.startCreate();
        }
        this.load();
      },
      error: () => (this.error = 'Suppression impossible.'),
    });
  }
}
