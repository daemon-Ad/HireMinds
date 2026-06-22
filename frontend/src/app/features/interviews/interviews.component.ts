import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InterviewService } from './interview.service';
import { Interview } from '../../core/models/models.interface';

@Component({
  selector: 'app-interviews',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './interviews.component.html',
  styleUrl: './interviews.component.scss'
})
export class InterviewsComponent implements OnInit {
  loading = signal(true);
  interviews = signal<Interview[]>([]);

  constructor(private interviewService: InterviewService) {}

  ngOnInit() {
    this.interviewService.listInterviews().subscribe({
      next: (interviews) => { this.interviews.set(interviews); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  getStatusClass(status: string): string {
    if (status === 'ACCEPTED') return 'success';
    if (status === 'DECLINED') return 'danger';
    return 'warning';
  }

  getStatusIcon(status: string): string {
    if (status === 'ACCEPTED') return 'check_circle';
    if (status === 'DECLINED') return 'cancel';
    return 'schedule';
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  }
}
