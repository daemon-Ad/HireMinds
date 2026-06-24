import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { JdService } from './jd.service';
import { JobDescription, parseSkills } from '../../core/models/models.interface';

@Component({
  selector: 'app-job-descriptions',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './job-descriptions.component.html',
  styleUrl: './job-descriptions.component.scss'
})
export class JobDescriptionsComponent implements OnInit {
  loading = signal(true);
  uploading = signal(false);
  showUploadPanel = signal(false);
  jds = signal<JobDescription[]>([]);
  searchQuery = signal('');
  error = signal('');
  success = signal('');

  displayJDs = computed(() => {
    let list = this.jds();
    const query = this.searchQuery().trim().toLowerCase();
    
    if (query) {
      list = list.filter(jd => 
        (jd.title && jd.title.toLowerCase().includes(query)) ||
        (jd.raw_text && jd.raw_text.toLowerCase().includes(query))
      );
    }
    
    return [...list].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  });

  // Upload form
  uploadTitle = '';
  uploadText = '';
  uploadFile: File | null = null;
  dragOver = false;

  constructor(private jdService: JdService) {}

  ngOnInit() {
    this.loadJDs();
  }

  loadJDs() {
    this.loading.set(true);
    this.jdService.listJDs().subscribe({
      next: (jds) => { this.jds.set(jds); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.dragOver = true;
  }

  onDragLeave() { this.dragOver = false; }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.dragOver = false;
    const file = event.dataTransfer?.files[0];
    if (file && file.type === 'application/pdf') {
      this.uploadFile = file;
    }
  }

  onFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.[0]) this.uploadFile = input.files[0];
  }

  onSubmit() {
    if (!this.uploadTitle) { this.error.set('Title is required.'); return; }
    if (!this.uploadFile && !this.uploadText) { this.error.set('Please provide a JD text or upload a PDF.'); return; }

    this.uploading.set(true);
    this.error.set('');

    const req$ = this.uploadFile
      ? this.jdService.uploadJDFile(this.uploadTitle, this.uploadFile)
      : this.jdService.uploadJD(this.uploadTitle, this.uploadText);

    req$.subscribe({
      next: (jd) => {
        this.jds.update(list => [jd, ...list]);
        this.success.set(`"${jd.title}" uploaded and parsed successfully!`);
        this.resetForm();
        this.uploading.set(false);
        setTimeout(() => this.success.set(''), 4000);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Upload failed.');
        this.uploading.set(false);
      }
    });
  }

  resetForm() {
    this.uploadTitle = '';
    this.uploadText = '';
    this.uploadFile = null;
    this.showUploadPanel.set(false);
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  getSkills(jd: JobDescription): string[] {
    return parseSkills(jd.required_skills);
  }
}
