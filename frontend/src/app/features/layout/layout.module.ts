import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { FrontShellComponent } from './pages/front-shell/front-shell.component';

const routes: Routes = [
  {
    path: '',
    component: FrontShellComponent,
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'home' },
      {
        path: 'home',
        loadChildren: () =>
          import('../resources/resources.module').then((m) => m.ResourcesModule),
      },
    ],
  },
];

@NgModule({
  declarations: [FrontShellComponent],
  imports: [SharedModule, RouterModule.forChild(routes)],
})
export class LayoutModule {}
