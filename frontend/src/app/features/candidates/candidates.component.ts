import { Component, OnInit, signal, computed, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterLink, ActivatedRoute, RouterModule } from '@angular/router';
import { CandidateService } from './candidate.service';
import { InterviewService } from '../interviews/interview.service';
import { JdService } from '../job-descriptions/jd.service';
import { CandidateMatch, JobDescription } from '../../core/models/models.interface';
import { DatetimePickerDirective } from '../../shared/directives/datetime-picker.directive';

@Component({
  selector: 'app-candidates',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, ReactiveFormsModule, DatetimePickerDirective],
  templateUrl: './candidates.component.html',
  styleUrl: './candidates.component.scss'
})
export class CandidatesComponent implements OnInit {
  jdId = signal('');
  jd = signal<JobDescription | null>(null);
  loading = signal(true);
  uploading = signal(false);
  sendingInterviews = signal(false);
  activeTab = signal<'shortlisted' | 'all'>('shortlisted');
  candidates = signal<CandidateMatch[]>([]);
  error = signal('');
  success = signal('');
  showUploadPanel = signal(false);
  showSlotPicker = signal(false);
  selectedCandidateId = signal<string | null>(null);
  expandedCandidateId = signal<string | null>(null);

  // Edit Title
  isEditingTitle = signal(false);
  savingTitle = signal(false);
  editTitleStr = '';

  // CV Upload
  cvFile: File | null = null;

  // Interview slots
  slots: { datetime: string }[] = [
    { datetime: '' },
    { datetime: '' },
    { datetime: '' }
  ];

  searchQuery = signal('');
  sortBy = signal<'score' | 'time'>('score');

  // Computed
  // Scores from backend are 0-1 fractions; shortlist threshold = 0.80
  shortlisted = computed(() => this.candidates().filter(c => c.overall_score >= 0.80));
  allCandidates = computed(() => this.candidates());
  displayCandidates = computed(() => {
    let list = this.activeTab() === 'shortlisted' ? this.shortlisted() : this.allCandidates();
    
    const query = this.searchQuery().trim().toLowerCase();
    if (query) {
      list = list.filter(c => 
        (c.name && c.name.toLowerCase().includes(query)) ||
        (c.email && c.email.toLowerCase().includes(query))
      );
    }

    return [...list].sort((a, b) => {
      if (this.sortBy() === 'score') {
        return b.overall_score - a.overall_score;
      } else {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
    });
  });

  constructor(
    private route: ActivatedRoute,
    private candidateService: CandidateService,
    private interviewService: InterviewService,
    private jdService: JdService
  ) {}

  ngOnInit() {
    const jdId = this.route.snapshot.paramMap.get('jd_id') || '';
    this.jdId.set(jdId);
    this.jdService.getJD(jdId).subscribe(jd => this.jd.set(jd));
    this.loadCandidates();
  }

  loadCandidates() {
    this.loading.set(true);
    this.candidateService.getRankedCandidates(this.jdId()).subscribe({
      next: (candidates) => { this.candidates.set(candidates); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  onFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.[0]) this.cvFile = input.files[0];
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    const file = event.dataTransfer?.files[0];
    if (file && file.type === 'application/pdf') this.cvFile = file;
  }

  uploadCV() {
    if (!this.cvFile) return;
    this.uploading.set(true);
    this.error.set('');
    this.candidateService.uploadCV(this.cvFile).subscribe({
      next: () => {
        this.success.set('CV uploaded! AI is matching candidates…');
        this.cvFile = null;
        this.showUploadPanel.set(false);
        this.uploading.set(false);
        setTimeout(() => { this.success.set(''); this.loadCandidates(); }, 2500);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Upload failed.');
        this.uploading.set(false);
      }
    });
  }

  openSlotPicker(candidateId?: string) {
    this.selectedCandidateId.set(candidateId || null);
    this.showSlotPicker.set(true);
  }

  toggleExpand(candidateId: string) {
    if (this.expandedCandidateId() === candidateId) {
      this.expandedCandidateId.set(null);
    } else {
      this.expandedCandidateId.set(candidateId);
    }
  }

  sendInterviews() {
    const validSlots = this.slots.filter(s => s.datetime).map(s => s.datetime);
      
    if (validSlots.length === 0) { this.error.set('Add at least one complete proposed interview slot (Date + Time).'); return; }
    this.sendingInterviews.set(true);
    
    const candidateId = this.selectedCandidateId() || undefined;
    this.interviewService.sendInterviews(this.jdId(), validSlots, candidateId).subscribe({
      next: (interviews) => {
        this.success.set(`${interviews.length} interview invitation(s) sent successfully!`);
        this.showSlotPicker.set(false);
        this.selectedCandidateId.set(null);
        this.sendingInterviews.set(false);
        setTimeout(() => this.success.set(''), 5000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Failed to send interviews.');
        this.sendingInterviews.set(false);
      }
    });
  }

  startEditingTitle() {
    this.editTitleStr = this.jd()?.title || '';
    this.isEditingTitle.set(true);
  }

  saveTitle() {
    if (!this.editTitleStr.trim()) return;
    this.savingTitle.set(true);
    this.jdService.updateJDTitle(this.jdId(), this.editTitleStr.trim()).subscribe({
      next: (updatedJd) => {
        this.jd.set(updatedJd);
        this.isEditingTitle.set(false);
        this.savingTitle.set(false);
        this.success.set('JD name updated successfully!');
        setTimeout(() => this.success.set(''), 3000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Failed to update JD name.');
        this.savingTitle.set(false);
      }
    });
  }

  getScoreClass(score: number): string {
    const pct = score > 1 ? score : score * 100; // handle both fraction and %
    if (pct >= 80) return 'high';
    if (pct >= 60) return 'good';
    if (pct >= 45) return 'mid';
    return 'low';
  }

  toPercent(score: number | undefined): number {
    if (score === undefined || score === null) return 0;
    // Backend returns 0-1 fractions
    return Math.round((score > 1 ? score : score * 100));
  }

  getSkills(match: CandidateMatch): string[] {
    if (!match.skills) return [];
    try { return JSON.parse(match.skills); } catch { return []; }
  }

  getInitials(name: string): string {
    if (!name || name === 'Unknown') return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  }
}
