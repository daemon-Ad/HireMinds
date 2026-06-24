import { Component, OnInit, signal } from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { CandidateService } from './candidate.service';

@Component({
  selector: 'app-candidate-profile',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './candidate-profile.component.html',
  styleUrl: './candidate-profile.component.scss'
})
export class CandidateProfileComponent implements OnInit {
  candidateId = signal('');
  candidate = signal<any>(null);
  loading = signal(true);
  error = signal('');

  constructor(
    private route: ActivatedRoute,
    private candidateService: CandidateService,
    private location: Location
  ) {}

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.candidateId.set(id);
      this.loadProfile();
    }
  }

  loadProfile() {
    this.loading.set(true);
    this.candidateService.getCandidateProfile(this.candidateId()).subscribe({
      next: (data) => {
        this.candidate.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Failed to load candidate profile.');
        this.loading.set(false);
      }
    });
  }

  getSkills(): string[] {
    const c = this.candidate();
    if (!c || !c.skills) return [];
    try { return JSON.parse(c.skills); } catch { return []; }
  }

  getExperience(): any[] {
    const c = this.candidate();
    if (!c || !c.experience_json) return [];
    try { return JSON.parse(c.experience_json); } catch { return []; }
  }

  getEducation(): any[] {
    const c = this.candidate();
    if (!c || !c.education_json) return [];
    try { return JSON.parse(c.education_json); } catch { return []; }
  }

  getInitials(name: string): string {
    if (!name || name === 'Unknown') return '?';
    return name.split(' ').map((n: string) => n[0]).join('').toUpperCase().slice(0, 2);
  }

  goBack() {
    this.location.back();
  }
}
