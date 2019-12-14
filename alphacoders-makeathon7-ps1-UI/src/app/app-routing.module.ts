import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { UploadComponent } from './upload/upload.component';
import { TeamComponent } from './team/team.component';
import { HomeComponent } from './home/home.component';
import { CardsComponent } from './cards/cards.component';


const routes: Routes = [
  { path : 'upload', component:UploadComponent},
  { path : 'team', component:TeamComponent},
  { path : 'home', component:HomeComponent},
  { path : 'solutions', component:CardsComponent},
  { path: '',
    redirectTo: '/home',
    pathMatch: 'full'
  },

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
