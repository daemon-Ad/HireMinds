import { Component, ElementRef, ViewChild, AfterViewInit, OnDestroy, HostListener } from '@angular/core';

@Component({
  selector: 'app-gravity-particles',
  standalone: true,
  template: `
    <div class="animation-container">
      <h2>Gravity Particles</h2>
      <p class="text-muted">Particles fall and bounce. Click to scatter them.</p>
      <canvas #canvas (click)="onClick($event)"></canvas>
    </div>
  `,
  styles: [`
    .animation-container { display: flex; flex-direction: column; height: 100%; padding: 1rem; }
    canvas { flex: 1; width: 100%; background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius-lg); margin-top: 1rem; cursor: pointer; }
  `]
})
export class GravityParticlesComponent implements AfterViewInit, OnDestroy {
  @ViewChild('canvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  private ctx!: CanvasRenderingContext2D;
  private animationFrameId: number = 0;
  private particles: any[] = [];
  private gravity = 0.5;
  private friction = 0.8;

  ngAfterViewInit() {
    this.initCanvas();
    this.createParticles();
    this.animate();
  }
  ngOnDestroy() { cancelAnimationFrame(this.animationFrameId); }
  @HostListener('window:resize') onResize() { this.initCanvas(); }

  onClick(event: MouseEvent) {
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    const mx = event.clientX - rect.left;
    const my = event.clientY - rect.top;

    this.particles.forEach(p => {
      const dx = p.x - mx;
      const dy = p.y - my;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 150) {
        const angle = Math.atan2(dy, dx);
        const force = (150 - dist) * 0.2;
        p.vx += Math.cos(angle) * force;
        p.vy += Math.sin(angle) * force;
      }
    });
  }

  private initCanvas() {
    const canvas = this.canvasRef.nativeElement;
    canvas.width = canvas.parentElement?.clientWidth || 800;
    canvas.height = canvas.parentElement?.clientHeight || 600;
    this.ctx = canvas.getContext('2d')!;
  }

  private createParticles() {
    for (let i = 0; i < 150; i++) {
      this.particles.push({
        x: Math.random() * this.canvasRef.nativeElement.width,
        y: Math.random() * this.canvasRef.nativeElement.height - this.canvasRef.nativeElement.height,
        vx: (Math.random() - 0.5) * 5,
        vy: Math.random() * 5,
        radius: Math.random() * 4 + 2
      });
    }
  }

  private animate = () => {
    this.animationFrameId = requestAnimationFrame(this.animate);
    const canvas = this.canvasRef.nativeElement;
    this.ctx.clearRect(0, 0, canvas.width, canvas.height);

    this.particles.forEach(p => {
      p.vy += this.gravity;
      p.x += p.vx;
      p.y += p.vy;

      if (p.y + p.radius > canvas.height) {
        p.y = canvas.height - p.radius;
        p.vy *= -this.friction;
        p.vx *= 0.95; // some horizontal friction on ground
      }
      if (p.x + p.radius > canvas.width) {
        p.x = canvas.width - p.radius;
        p.vx *= -this.friction;
      } else if (p.x - p.radius < 0) {
        p.x = p.radius;
        p.vx *= -this.friction;
      }

      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = '#00aa00';
      this.ctx.fill();
    });
  }
}
