import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-service-unavailable',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './service-unavailable.component.html',
  styleUrl: './service-unavailable.component.scss'
})
export class ServiceUnavailableComponent {
  constructor(private router: Router) {}

  retryConnection() {
    // Navigate back to dashboard to retry fetching data
    this.router.navigate(['/dashboard']);
  }
}
