import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  template: `
    <div class="container">
      <h1>{{ title }}</h1>
      <p>{{ message }}</p>
      <button (click)="fetchData()">Fetch Data</button>
      <div *ngIf="data">
        <pre>{{ data | json }}</pre>
      </div>
    </div>
  `,
  styles: [`
    .container {
      padding: 20px;
      text-align: center;
    }
  `]
})
export class AppComponent {
  title = 'Angular Docker App';
  message = 'Welcome to Angular with Docker!';
  data: any;

  constructor(private http: HttpClient) {}

  fetchData() {
    this.http.get('/api/info').subscribe(
      response => this.data = response,
      error => console.error('Error:', error)
    );
  }
}
