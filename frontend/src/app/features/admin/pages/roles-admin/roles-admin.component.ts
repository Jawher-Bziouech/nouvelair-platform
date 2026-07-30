import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { RoleService } from '../../../../core/services/role.service';
import { Role } from '../../../../core/models/api.models';

@Component({
  selector: 'app-roles-admin',
  standalone: false,
  templateUrl: './roles-admin.component.html',
  styleUrl: './roles-admin.component.scss',
})
export class RolesAdminComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly roleService = inject(RoleService);

  roles: Role[] = [];
  error = '';
  editingId: number | null = null;

  form = this.fb.group({
    nom: ['', Validators.required],
  });

  ngOnInit(): void {
    this.load();
  }

  get isEditing(): boolean {
    return this.editingId !== null;
  }

  load(): void {
    this.roleService.list().subscribe({
      next: (roles: Role[]) => (this.roles = roles),
      error: () => (this.error = 'Impossible de charger les rôles.'),
    });
  }

  startCreate(): void {
    this.editingId = null;
    this.error = '';
    this.form.reset();
  }

  startEdit(role: Role): void {
    this.editingId = role.id;
    this.error = '';
    this.form.setValue({ nom: role.nom });
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const nom = this.form.value.nom!;
    if (this.editingId === null) {
      this.roleService.create(nom).subscribe({
        next: () => {
          this.startCreate();
          this.load();
        },
        error: () => (this.error = 'Création impossible.'),
      });
      return;
    }

    this.roleService.update(this.editingId, nom).subscribe({
      next: () => {
        this.startCreate();
        this.load();
      },
      error: () => (this.error = 'Mise à jour impossible.'),
    });
  }

  remove(role: Role): void {
    if (!confirm(`Supprimer le rôle ${role.nom} ?`)) {
      return;
    }
    this.roleService.delete(role.id).subscribe({
      next: () => {
        if (this.editingId === role.id) {
          this.startCreate();
        }
        this.load();
      },
      error: () => (this.error = 'Suppression impossible (rôle encore utilisé).'),
    });
  }
}
