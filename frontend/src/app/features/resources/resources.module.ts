import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { roleGuard } from '../../core/guards/role.guard';
import { ResourceListComponent } from './pages/resource-list/resource-list.component';
import { ResourceUploadComponent } from './pages/resource-upload/resource-upload.component';
import { ResourceDetailComponent } from './pages/resource-detail/resource-detail.component';

const routes: Routes = [
  { path: '', component: ResourceListComponent },
  {
    path: 'upload',
    canActivate: [roleGuard('Administrateur', 'Manager')],
    component: ResourceUploadComponent,
  },
  { path: ':id', component: ResourceDetailComponent },
];

@NgModule({
  declarations: [
    ResourceListComponent,
    ResourceUploadComponent,
    ResourceDetailComponent,
  ],
  imports: [SharedModule, RouterModule.forChild(routes)],
})
export class ResourcesModule {}
