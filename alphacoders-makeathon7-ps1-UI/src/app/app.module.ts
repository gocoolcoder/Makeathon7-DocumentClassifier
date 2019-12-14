import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NavbarComponent } from './navbar/navbar.component';
import {MatToolbarModule} from '@angular/material/toolbar';
import { UploadComponent } from './upload/upload.component';
import {MatButtonModule} from '@angular/material/button';
import { HttpClientModule } from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import { FileUploadModule } from 'ng2-file-upload';
import { TeamComponent } from './team/team.component';
import { HomeComponent } from './home/home.component';
import { NgxSpinnerModule } from "ngx-spinner";
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatTableModule} from '@angular/material/table';
import { CardsComponent } from './cards/cards.component';
import {MatCardModule} from '@angular/material/card';


@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    UploadComponent,
    TeamComponent,
    HomeComponent,
    CardsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    MatToolbarModule,
    MatButtonModule,
    HttpClientModule,
    FormsModule,
    FileUploadModule,
    NgxSpinnerModule,
    MatSnackBarModule,
    MatTableModule,
    MatCardModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
