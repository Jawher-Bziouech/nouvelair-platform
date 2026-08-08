import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { AssistantChatComponent } from './pages/assistant-chat/assistant-chat.component';

const routes: Routes = [{ path: '', component: AssistantChatComponent }];

@NgModule({
  declarations: [AssistantChatComponent],
  imports: [SharedModule, RouterModule.forChild(routes)],
})
export class AssistantModule {}
