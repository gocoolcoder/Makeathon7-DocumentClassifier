import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { UploadComponent } from './upload/upload.component';
import { TeamComponent } from './team/team.component';
import { HomeComponent } from './home/home.component';
import { JobsComponent } from './jobs/jobs.component';


const routes: Routes = [
  { path : 'upload', component:UploadComponent},
  { path : 'jobs', component:JobsComponent},
  { path : 'team', component:TeamComponent},
  { path : 'home', component:HomeComponent},
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
