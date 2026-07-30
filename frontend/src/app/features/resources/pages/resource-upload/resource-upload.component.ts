import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { CategorieService } from '../../../../core/services/categorie.service';
import { RessourceService } from '../../../../core/services/ressource.service';
import { Categorie, Ressource } from '../../../../core/models/api.models';

@Component({
  selector: 'app-resource-upload',
  standalone: false,
  templateUrl: './resource-upload.component.html',
  styleUrl: './resource-upload.component.scss',
})
export class ResourceUploadComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly categorieService = inject(CategorieService);
  private readonly ressourceService = inject(RessourceService);
  private readonly router = inject(Router);

  categories: Categorie[] = [];
  selectedFile: File | null = null;
  error = '';
  success = '';
  loading = false;

  form = this.fb.group({
    titre: ['', Validators.required],
    type: ['blog', Validators.required],
    categorie_id: [null as number | null, Validators.required],
    contenu: [''],
  });

  ngOnInit(): void {
    this.categorieService.list().subscribe({
      next: (cats: Categorie[]) => (this.categories = cats),
      error: () => (this.error = 'Impossible de charger les catégories.'),
    });
  }

  onFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile = input.files?.[0] || null;
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const value = this.form.getRawValue();
    const contenu = (value.contenu || '').trim() || null;
    this.loading = true;
    this.error = '';
    this.success = '';

    let request$: Observable<Ressource>;

    if (this.selectedFile) {
      const formData = new FormData();
      formData.append('titre', value.titre!);
      formData.append('type', value.type!);
      formData.append('categorie_id', String(value.categorie_id));
      if (contenu) {
        formData.append('contenu', contenu);
      }
      formData.append('file', this.selectedFile);
      request$ = this.ressourceService.upload(formData);
    } else {
      request$ = this.ressourceService.create({
        titre: value.titre!,
        type: value.type!,
        categorie_id: value.categorie_id!,
        contenu,
      });
    }

    request$.subscribe({
      next: () => {
        this.loading = false;
        this.success = 'Ressource ajoutée.';
        this.router.navigate(['/home']);
      },
      error: () => {
        this.loading = false;
        this.error = "Échec de l'enregistrement.";
      },
    });
  }
}
