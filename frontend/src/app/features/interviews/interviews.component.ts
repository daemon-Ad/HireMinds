import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { InterviewService } from './interview.service';
import { Interview } from '../../core/models/models.interface';
import { DatetimePickerDirective } from '../../shared/directives/datetime-picker.directive';

@Component({
  selector: 'app-interviews',
  standalone: true,
  imports: [CommonModule, FormsModule, DatetimePickerDirective],
  templateUrl: './interviews.component.html',
  styleUrl: './interviews.component.scss'
})
export class InterviewsComponent implements OnInit {
  loading = signal(true);
  interviews = signal<Interview[]>([]);
  activeTab = signal<'active' | 'past' | 'postponed' | 'cancelled'>('active');

  // Modal state
  showModal = signal(false);
  modalAction = signal<'cancel' | 'postpone'>('cancel');
  selectedInterview = signal<Interview | null>(null);
  
  slots: { datetime: string }[] = [{ datetime: '' }];
  updating = signal(false);
  error = signal('');
  success = signal('');

  // Computed
  activeInterviews = computed(() => this.interviews().filter(i => {
    const s = i.status.toLowerCase();
    if (!['pending', 'sent', 'accepted'].includes(s)) return false;
    const slots = this.getParsedSlots(i.proposed_slots);
    const now = new Date();
    // Active if at least one slot is in the future
    return slots.length === 0 || slots.some(slot => new Date(slot) >= now);
  }));

  pastInterviews = computed(() => this.interviews().filter(i => {
    const s = i.status.toLowerCase();
    if (['rejected', 'failed'].includes(s)) return true;
    if (['pending', 'sent', 'accepted'].includes(s)) {
      const slots = this.getParsedSlots(i.proposed_slots);
      const now = new Date();
      // Past if all slots are in the past
      return slots.length > 0 && slots.every(slot => new Date(slot) < now);
    }
    return false;
  }));

  postponedInterviews = computed(() => this.interviews().filter(i => i.status.toLowerCase() === 'postponed'));
  cancelledInterviews = computed(() => this.interviews().filter(i => i.status.toLowerCase() === 'cancelled'));

  displayInterviews = computed(() => {
    switch (this.activeTab()) {
      case 'active': return this.activeInterviews();
      case 'past': return this.pastInterviews();
      case 'postponed': return this.postponedInterviews();
      case 'cancelled': return this.cancelledInterviews();
      default: return this.activeInterviews();
    }
  });

  constructor(private interviewService: InterviewService) {}

  ngOnInit() {
    this.loadInterviews();
  }

  loadInterviews() {
    this.loading.set(true);
    this.interviewService.listInterviews().subscribe({
      next: (interviews) => { this.interviews.set(interviews); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  getStatusClass(status: string): string {
    const s = status.toLowerCase();
    if (s === 'accepted') return 'success';
    if (s === 'declined' || s === 'rejected' || s === 'cancelled') return 'danger';
    if (s === 'postponed') return 'warning';
    return 'primary';
  }

  formatDate(dateStr: string): string {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  }

  getParsedSlots(slotsStr: string | null): string[] {
    if (!slotsStr) return [];
    try {
      return JSON.parse(slotsStr);
    } catch {
      return [slotsStr];
    }
  }

  openModal(interview: Interview, action: 'cancel' | 'postpone') {
    this.selectedInterview.set(interview);
    this.modalAction.set(action);
    this.slots = [{ datetime: '' }];
    this.error.set('');
    this.showModal.set(true);
  }

  closeModal() {
    this.showModal.set(false);
    this.selectedInterview.set(null);
  }

  submitUpdate() {
    const interview = this.selectedInterview();
    if (!interview) return;

    let validSlots: string[] = [];
    if (this.modalAction() === 'postpone') {
      validSlots = this.slots.filter(s => s.datetime).map(s => s.datetime);
      if (validSlots.length === 0) {
        this.error.set('Please provide at least one new time slot.');
        return;
      }
    }

    this.updating.set(true);
    this.error.set('');
    
    this.interviewService.updateInterview(interview.interview_id, this.modalAction(), validSlots).subscribe({
      next: () => {
        this.success.set(`Interview ${this.modalAction()}ed successfully.`);
        this.updating.set(false);
        this.closeModal();
        this.loadInterviews();
        setTimeout(() => this.success.set(''), 3000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Failed to update interview.');
        this.updating.set(false);
      }
    });
  }
}
