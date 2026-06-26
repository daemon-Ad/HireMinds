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
  private particles: {x: number, y: number, vx: number, vy: number, radius: number}[] = [];
  private mouse = { x: -1000, y: -1000 };

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
    this.mouse.x = event.clientX - rect.left;
    this.mouse.y = event.clientY - rect.top;
  }

  @HostListener('mouseleave')
  onMouseLeave() {
    this.mouse.x = -1000;
    this.mouse.y = -1000;
  }

  private initCanvas() {
    const canvas = this.canvasRef.nativeElement;
    canvas.width = canvas.parentElement?.clientWidth || window.innerWidth;
    canvas.height = canvas.parentElement?.clientHeight || window.innerHeight;
    this.ctx = canvas.getContext('2d')!;

    this.particles = [];
    const numParticles = Math.floor((canvas.width * canvas.height) / 12000);
    for (let i = 0; i < numParticles; i++) {
      this.particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5,
        radius: Math.random() * 2 + 1
      });
    }
  }

  private animate = () => {
    this.animationFrameId = requestAnimationFrame(this.animate);
    const canvas = this.canvasRef.nativeElement;
    this.ctx.clearRect(0, 0, canvas.width, canvas.height);

    const maxDistance = 150;
    
    this.particles.forEach((p, i) => {
      p.x += p.vx;
      p.y += p.vy;
      
      if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = 'rgba(0, 255, 0, 0.6)';
      this.ctx.fill();
      
      for (let j = i + 1; j < this.particles.length; j++) {
        const p2 = this.particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist < maxDistance) {
          this.ctx.beginPath();
          this.ctx.moveTo(p.x, p.y);
          this.ctx.lineTo(p2.x, p2.y);
          const opacity = 1 - (dist / maxDistance);
          this.ctx.strokeStyle = `rgba(0, 255, 0, ${opacity * 0.4})`;
          this.ctx.lineWidth = 1.5;
          this.ctx.stroke();
        }
      }
      
      const mdx = p.x - this.mouse.x;
      const mdy = p.y - this.mouse.y;
      const mDist = Math.sqrt(mdx * mdx + mdy * mdy);
      
      if (mDist < 200) {
        this.ctx.beginPath();
        this.ctx.moveTo(p.x, p.y);
        this.ctx.lineTo(this.mouse.x, this.mouse.y);
        const mOpacity = 1 - (mDist / 200);
        this.ctx.strokeStyle = `rgba(0, 255, 0, ${mOpacity * 0.6})`;
        this.ctx.lineWidth = 1.5;
        this.ctx.stroke();
      }
    });
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
