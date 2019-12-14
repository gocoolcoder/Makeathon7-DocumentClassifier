import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';

import { NgxSpinnerService } from "ngx-spinner";


@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.scss']
})
export class UploadComponent implements OnInit {
  fileToUpload: File[] = [];
  displayedColumns: string[] = ['order', 'invoice', 'document_tag', 'path', 'filename', 'quantity'];
  dataSource : any = [];

  constructor(private http: HttpClient, private spinner: NgxSpinnerService, private _snackBar: MatSnackBar) {
      this.getDocuments();
  }

  ngOnInit() {
  }

  handleFileInput(files: FileList) {
    this.fileToUpload = []
    for (var i = 0; i < files.length; i++) {
      this.fileToUpload.push(files.item(i));

    }
  }

  postFile() {
    if (this.fileToUpload.length > 0) {
      var formData: FormData = new FormData();
      for (var i = 0; i < this.fileToUpload.length; i++) {
        formData.append('file' + i, this.fileToUpload[i], this.fileToUpload[i].name);

      }
      this.spinner.show();
      this.http
        .post('http://localhost:5000/upload_files', formData, { responseType: "text" })
        .subscribe(data => {
         
          data = JSON.parse(data)
          console.log(data)
          this._snackBar.open(data["message"], "", {
            duration: 2000,
          });
          this.getDocuments();
        })
      
    }
    else {
      this._snackBar.open("Please select files", "OK", {
        duration: 2000,
      });
    }

  }

  getDocuments(){
    this.http.get('http://localhost:3000/api/documents')
          .subscribe(
            data => {
              this.dataSource = new Array();
              this.spinner.hide();
              this.dataSource = data;
              console.log(data)
            }
          )
  }

  deleteAll(){
    this.spinner.show();
    this.http.delete('http://localhost:5000/delete')
    .subscribe(
      data =>{
        console.log(data);
        this.spinner.hide();
        this.getDocuments();
      }
    )
  }



}
