import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { RoleService } from '../../../../core/services/role.service';
import { UserService } from '../../../../core/services/user.service';
import { Role, User } from '../../../../core/models/api.models';

@Component({
  selector: 'app-users-admin',
  standalone: false,
  templateUrl: './users-admin.component.html',
  styleUrl: './users-admin.component.scss',
})
export class UsersAdminComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly userService = inject(UserService);
  private readonly roleService = inject(RoleService);

  users: User[] = [];
  roles: Role[] = [];
  error = '';
  editingId: number | null = null;

  form = this.fb.group({
    nom: ['', Validators.required],
    prenom: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    mot_de_passe: [''],
    role_id: [null as number | null, Validators.required],
  });

  ngOnInit(): void {
    this.roleService.list().subscribe({
      next: (roles: Role[]) => (this.roles = roles),
    });
    this.load();
  }

  get isEditing(): boolean {
    return this.editingId !== null;
  }

  load(): void {
    this.userService.list().subscribe({
      next: (users: User[]) => (this.users = users),
      error: () => (this.error = 'Impossible de charger les utilisateurs.'),
    });
  }

  startCreate(): void {
    this.editingId = null;
    this.error = '';
    this.form.reset({ role_id: null, mot_de_passe: '' });
    this.form.controls.mot_de_passe.setValidators([Validators.required]);
    this.form.controls.mot_de_passe.updateValueAndValidity();
  }

  startEdit(user: User): void {
    this.editingId = user.id;
    this.error = '';
    this.form.setValue({
      nom: user.nom,
      prenom: user.prenom,
      email: user.email,
      mot_de_passe: '',
      role_id: user.role_id,
    });
    this.form.controls.mot_de_passe.clearValidators();
    this.form.controls.mot_de_passe.updateValueAndValidity();
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const value = this.form.getRawValue();

    if (this.editingId === null) {
      this.userService
        .create({
          nom: value.nom!,
          prenom: value.prenom!,
          email: value.email!,
          mot_de_passe: value.mot_de_passe!,
          role_id: value.role_id!,
        })
        .subscribe({
          next: () => {
            this.startCreate();
            this.load();
          },
          error: () => (this.error = 'Création utilisateur impossible.'),
        });
      return;
    }

    const payload: Partial<{
      nom: string;
      prenom: string;
      email: string;
      mot_de_passe: string;
      role_id: number;
    }> = {
      nom: value.nom!,
      prenom: value.prenom!,
      email: value.email!,
      role_id: value.role_id!,
    };
    if (value.mot_de_passe) {
      payload.mot_de_passe = value.mot_de_passe;
    }

    this.userService.update(this.editingId, payload).subscribe({
      next: () => {
        this.startCreate();
        this.load();
      },
      error: () => (this.error = 'Mise à jour impossible.'),
    });
  }

  remove(user: User): void {
    if (!confirm(`Supprimer ${user.email} ?`)) {
      return;
    }
    this.userService.delete(user.id).subscribe({
      next: () => {
        if (this.editingId === user.id) {
          this.startCreate();
        }
        this.load();
      },
      error: () => (this.error = 'Suppression impossible.'),
    });
  }
}
