import { Component, HostListener, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';

@Component({
  selector: 'app-about',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './about.component.html',
  styleUrl: './about.component.scss'
})
export class AboutComponent {
  constructor(public auth: AuthService, private el: ElementRef) {}

  @HostListener('mousemove', ['$event'])
  onMouseMove(event: MouseEvent) {
    const { clientX, clientY } = event;
    this.el.nativeElement.style.setProperty('--mouse-x', `${clientX}px`);
    this.el.nativeElement.style.setProperty('--mouse-y', `${clientY}px`);
  }

  steps = [
    { icon: 'upload_file',    title: 'Upload JD',       desc: 'Paste or upload your job description PDF' },
    { icon: 'auto_awesome',   title: 'AI Parsing',      desc: 'Groq LLM extracts skills, experience, and requirements' },
    { icon: 'person_search',  title: 'CV Matching',     desc: 'Multi-agent scoring matches candidates by skills, experience & education' },
    { icon: 'calendar_month', title: 'Schedule',        desc: 'Auto-send interview invitations to shortlisted candidates (≥80%)' },
  ];

  techStack = [
    { name: 'FastAPI',      color: '#009688' },
    { name: 'Angular 19',   color: '#dd0031' },
    { name: 'PostgreSQL',   color: '#336791' },
    { name: 'Groq LLM',     color: '#f55036' },
    { name: 'SQLAlchemy',   color: '#d71f00' },
    { name: 'JWT Auth',     color: '#8b5cf6' },
  ];
}
