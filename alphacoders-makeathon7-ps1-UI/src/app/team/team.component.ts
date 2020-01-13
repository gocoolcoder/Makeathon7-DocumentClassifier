import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';



@Component({
  selector: 'app-team',
  templateUrl: './team.component.html',
  styleUrls: ['./team.component.scss']
})
export class TeamComponent implements OnInit {
  dataSource :any = [
    {
      'name': "Ashwathi",
      'email': "ash.wathi",
      'emp_id': "45688",
    }
  ];
  displayedColumns: string[];
  // displayedColumns: string[] = ['name','email','emp_id'];
  
  constructor(private http:HttpClient) { 
    

    this.http.get('http://localhost:3000/api/teams')
    .subscribe(
      data => {
        this.dataSource = data;
        this.displayedColumns = Object.keys(this.dataSource[0]);
        console.log(this.displayedColumns);
      }
    )

  }

  ngOnInit() {
  }

}
