import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { AdminShellComponent } from './pages/admin-shell/admin-shell.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { UsersAdminComponent } from './pages/users-admin/users-admin.component';
import { RolesAdminComponent } from './pages/roles-admin/roles-admin.component';
import { CategoriesAdminComponent } from './pages/categories-admin/categories-admin.component';

const routes: Routes = [
  {
    path: '',
    component: AdminShellComponent,
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'users', component: UsersAdminComponent },
      { path: 'roles', component: RolesAdminComponent },
      { path: 'categories', component: CategoriesAdminComponent },
    ],
  },
];

@NgModule({
  declarations: [
    AdminShellComponent,
    DashboardComponent,
    UsersAdminComponent,
    RolesAdminComponent,
    CategoriesAdminComponent,
  ],
  imports: [SharedModule, RouterModule.forChild(routes)],
})
export class AdminModule {}
