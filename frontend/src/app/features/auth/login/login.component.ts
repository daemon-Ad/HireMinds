import { Component, HostListener, signal, ElementRef, ViewChild, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent implements AfterViewInit, OnDestroy {
  activeTab = signal<'login' | 'register'>('login');
  loading = signal(false);
  error = signal('');

  // Login form
  loginEmail = '';
  loginPassword = '';

  // Register form
  regUsername = '';
  regEmail = '';
  regPassword = '';

  @ViewChild('networkCanvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  
  private ctx!: CanvasRenderingContext2D;
  private animationFrameId: number = 0;
  private points: {x: number, y: number, life: number}[] = [];

  constructor(private auth: AuthService, private router: Router) {
    if (this.auth.isLoggedIn()) {
      this.router.navigate(['/dashboard']);
    }
  }

  setTab(tab: 'login' | 'register') {
    this.activeTab.set(tab);
    this.error.set('');
  }

  @HostListener('window:keydown.escape', ['$event'])
  onEscape() {
    this.router.navigate(['/about']);
  }

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

  onLogin() {
    if (!this.loginEmail || !this.loginPassword) return;
    this.loading.set(true);
    this.error.set('');

    this.auth.login(this.loginEmail, this.loginPassword).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: (err) => {
        this.error.set(err.error?.detail || 'Login failed. Check your credentials.');
        this.loading.set(false);
      }
    });
  }

  onRegister() {
    if (!this.regUsername || !this.regEmail || !this.regPassword) return;
    this.loading.set(true);
    this.error.set('');

    this.auth.register({ username: this.regUsername, email: this.regEmail, password: this.regPassword }).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: (err) => {
        this.error.set(err.error?.detail || 'Registration failed. Try a different email.');
        this.loading.set(false);
      }
    });
  }
}
