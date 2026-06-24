import { Component, ElementRef, ViewChild, AfterViewInit, OnDestroy, HostListener } from '@angular/core';
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
export class AboutComponent implements AfterViewInit, OnDestroy {
  @ViewChild('networkCanvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  
  private ctx!: CanvasRenderingContext2D;
  private animationFrameId: number = 0;
  private points: {x: number, y: number, life: number}[] = [];

  constructor(public auth: AuthService) {}

  ngAfterViewInit() {
    this.initCanvas();
    this.animate();
  }

  ngOnDestroy() {
    cancelAnimationFrame(this.animationFrameId);
  }

  @HostListener('window:resize')
  onResize() {
    this.initCanvas();
  }

  @HostListener('mousemove', ['$event'])
  onMouseMove(event: MouseEvent) {
    if (!this.canvasRef) return;
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    this.points.push({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
      life: 1.0
    });
  }

  private initCanvas() {
    const canvas = this.canvasRef.nativeElement;
    canvas.width = canvas.parentElement?.clientWidth || window.innerWidth;
    canvas.height = canvas.parentElement?.clientHeight || window.innerHeight;
    this.ctx = canvas.getContext('2d')!;
  }

  private animate = () => {
    this.animationFrameId = requestAnimationFrame(this.animate);
    const canvas = this.canvasRef.nativeElement;
    this.ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (this.points.length === 0) return;

    this.ctx.beginPath();
    this.ctx.moveTo(this.points[0].x, this.points[0].y);
    for (let i = 1; i < this.points.length; i++) {
      this.ctx.lineTo(this.points[i].x, this.points[i].y);
    }
    
    this.ctx.strokeStyle = '#00aa00';
    this.ctx.lineWidth = 4;
    this.ctx.lineCap = 'round';
    this.ctx.lineJoin = 'round';
    this.ctx.stroke();

    for (let i = 0; i < this.points.length; i++) {
      this.points[i].life -= 0.02;
    }
    this.points = this.points.filter(p => p.life > 0);
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
