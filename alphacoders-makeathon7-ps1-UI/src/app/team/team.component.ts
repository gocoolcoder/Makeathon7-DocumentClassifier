import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-team',
  templateUrl: './team.component.html',
  styleUrls: ['./team.component.scss']
})
export class TeamComponent implements OnInit {
  dataSource :any = [];
  displayedColumns: string[] = ['name','email','emp_id'];

  constructor(private http:HttpClient) { 

    this.http.get('http://localhost:3000/api/teams')
    .subscribe(
      data => {
        this.dataSource = data;
      }
    )

  }

  ngOnInit() {
  }

}
