import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { JdService } from '../job-descriptions/jd.service';
import { CandidateService } from '../candidates/candidate.service';
import { InterviewService } from '../interviews/interview.service';

@Component({
  selector: 'app-archive',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './archive.component.html',
  styleUrl: './archive.component.scss'
})
export class ArchiveComponent implements OnInit {
  type = signal<'jds' | 'candidates' | 'interviews'>('jds');
  data = signal<any[]>([]);
  loading = signal(true);

  constructor(
    private route: ActivatedRoute,
    private location: Location,
    private jdService: JdService,
    private candidateService: CandidateService,
    private interviewService: InterviewService
  ) {}

  ngOnInit() {
    const type = this.route.snapshot.paramMap.get('type') as any;
    if (['jds', 'candidates', 'interviews'].includes(type)) {
      this.type.set(type);
      this.loadData();
    }
  }

  goBack() {
    this.location.back();
  }

  loadData() {
    this.loading.set(true);
    const type = this.type();
    
    if (type === 'jds') {
      this.jdService.listJDs().subscribe({
        next: (d) => { this.data.set(d); this.loading.set(false); },
        error: () => this.loading.set(false)
      });
    } else if (type === 'candidates') {
      this.candidateService.getAllCandidates().subscribe({
        next: (d) => { this.data.set(d); this.loading.set(false); },
        error: () => this.loading.set(false)
      });
    } else if (type === 'interviews') {
      this.interviewService.listInterviews().subscribe({
        next: (d) => { this.data.set(d); this.loading.set(false); },
        error: () => this.loading.set(false)
      });
    }
  }

  formatDate(dateStr: string): string {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleString();
  }

  formatScore(score: number | undefined): number {
    if (score === undefined || score === null) return 0;
    return Math.round((score > 1 ? score : score * 100));
  }
}
