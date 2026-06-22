import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { JdService } from '../job-descriptions/jd.service';
import { InterviewService } from '../interviews/interview.service';
import { JobDescription, Interview } from '../../core/models/models.interface';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  loading = signal(true);
  jds = signal<JobDescription[]>([]);
  interviews = signal<Interview[]>([]);

  get totalJDs()     { return this.jds().length; }
  get totalShortlisted() {
    // Shortlisted count comes from interviews sent (one per shortlisted candidate)
    return this.interviews().length;
  }
  get interviewsSent() { return this.interviews().length; }
  get recentJDs() { return this.jds().slice(0, 5); }

  constructor(
    private jdService: JdService,
    private interviewService: InterviewService
  ) {}

  ngOnInit() {
    forkJoin({
      jds: this.jdService.listJDs(),
      interviews: this.interviewService.listInterviews()
    }).subscribe({
      next: ({ jds, interviews }) => {
        this.jds.set(jds);
        this.interviews.set(interviews);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }
}
