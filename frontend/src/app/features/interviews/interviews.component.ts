import { Component, OnInit, signal, computed, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { InterviewService } from './interview.service';
import { Interview } from '../../core/models/models.interface';
import { DatetimePickerDirective } from '../../shared/directives/datetime-picker.directive';

@Component({
  selector: 'app-interviews',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, DatetimePickerDirective],
  templateUrl: './interviews.component.html',
  styleUrl: './interviews.component.scss'
})
export class InterviewsComponent implements OnInit {
  loading = signal(true);
  interviews = signal<Interview[]>([]);
  activeTab = signal<'active' | 'past' | 'cancelled'>('active');

  searchQuery = signal('');
  dateFilter = signal<'All' | 'Today' | 'This Week' | 'Next Week'>('All');
  isDateDropdownOpen = signal(false);

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
    // Active if at least one slot is in the future or unparseable
    return slots.length === 0 || slots.some(slot => {
      const d = new Date(slot);
      return isNaN(d.getTime()) || d >= now;
    });
  }));

  pastInterviews = computed(() => this.interviews().filter(i => {
    const s = i.status.toLowerCase();
    if (['rejected', 'failed'].includes(s)) return true;
    if (['pending', 'sent', 'accepted'].includes(s)) {
      const slots = this.getParsedSlots(i.proposed_slots);
      const now = new Date();
      // Past if all slots are in the past
      return slots.length > 0 && slots.every(slot => {
        const d = new Date(slot);
        return !isNaN(d.getTime()) && d < now;
      });
    }
    return false;
  }));

  cancelledInterviews = computed(() => this.interviews().filter(i => i.status.toLowerCase() === 'cancelled'));

  displayInterviews = computed(() => {
    let list: Interview[] = [];
    switch (this.activeTab()) {
      case 'active': list = this.activeInterviews(); break;
      case 'past': list = this.pastInterviews(); break;
      case 'cancelled': list = this.cancelledInterviews(); break;
      default: list = this.activeInterviews(); break;
    }

    const query = this.searchQuery().trim().toLowerCase();
    if (query) {
      list = list.filter(i => 
        (i.candidate_name && i.candidate_name.toLowerCase().includes(query)) ||
        (i.jd_title && i.jd_title.toLowerCase().includes(query))
      );
    }

    const dFilter = this.dateFilter();
    if (dFilter !== 'All') {
      const now = new Date();
      const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      
      list = list.filter(i => {
        const slots = this.getParsedSlots(i.proposed_slots)
          .map(s => new Date(s))
          .filter(d => d >= todayStart)
          .sort((a, b) => a.getTime() - b.getTime());
          
        if (slots.length === 0) return false;
        
        const nextSlot = slots[0];
        const diffDays = (nextSlot.getTime() - todayStart.getTime()) / (1000 * 60 * 60 * 24);
        
        if (dFilter === 'Today') return diffDays < 1;
        if (dFilter === 'This Week') return diffDays < 7;
        if (dFilter === 'Next Week') return diffDays >= 7 && diffDays < 14;
        return true;
      });
    }

    return list.slice(0, 100);
  });

  @HostListener('document:click')
  onDocumentClick() {
    if (this.isDateDropdownOpen()) {
      this.isDateDropdownOpen.set(false);
    }
  }

  toggleDateDropdown(event: Event) {
    event.stopPropagation();
    this.isDateDropdownOpen.set(!this.isDateDropdownOpen());
  }

  selectDateFilter(option: 'All' | 'Today' | 'This Week' | 'Next Week') {
    this.dateFilter.set(option);
    this.isDateDropdownOpen.set(false);
  }

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
