import { Component, ElementRef, ViewChild, AfterViewInit, OnDestroy, HostListener } from '@angular/core';

@Component({
  selector: 'app-particle-mesh',
  standalone: true,
  template: `
    <div class="animation-container">
      <h2>Particle Mesh</h2>
      <p class="text-muted">Original live network animation.</p>
      <canvas #canvas (mousemove)="onMouseMove($event)"></canvas>
    </div>
  `,
  styles: [`
    .animation-container { display: flex; flex-direction: column; height: 100%; padding: 1rem; }
    canvas { flex: 1; width: 100%; background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius-lg); margin-top: 1rem; }
  `]
})
export class ParticleMeshComponent implements AfterViewInit, OnDestroy {
  @ViewChild('canvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  
  private ctx!: CanvasRenderingContext2D;
  private particles: any[] = [];
  private animationFrameId: number = 0;
  private mouse = { x: 0, y: 0 };

  ngAfterViewInit() {
    this.initCanvas();
    this.createParticles();
    this.animate();
  }

  ngOnDestroy() {
    cancelAnimationFrame(this.animationFrameId);
  }

  @HostListener('window:resize')
  onResize() {
    this.initCanvas();
    this.createParticles();
  }

  onMouseMove(event: MouseEvent) {
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    this.mouse.x = event.clientX - rect.left;
    this.mouse.y = event.clientY - rect.top;
  }

  private initCanvas() {
    const canvas = this.canvasRef.nativeElement;
    canvas.width = canvas.parentElement?.clientWidth || 800;
    canvas.height = canvas.parentElement?.clientHeight || 600;
    this.ctx = canvas.getContext('2d')!;
  }

  private createParticles() {
    this.particles = [];
    const canvas = this.canvasRef.nativeElement;
    const numParticles = Math.min(80, (canvas.width * canvas.height) / 12000);
    for (let i = 0; i < numParticles; i++) {
      this.particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5,
        radius: Math.random() * 1.5 + 0.5
      });
    }
  }

  private animate = () => {
    this.animationFrameId = requestAnimationFrame(this.animate);
    const canvas = this.canvasRef.nativeElement;
    this.ctx.clearRect(0, 0, canvas.width, canvas.height);

    const maxDistance = 150;

    for (let i = 0; i < this.particles.length; i++) {
      let p = this.particles[i];

      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = 'rgba(0, 170, 0, 0.4)';
      this.ctx.fill();

      const dxMouse = this.mouse.x - p.x;
      const dyMouse = this.mouse.y - p.y;
      const distMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse);
      
      if (distMouse < maxDistance) {
        this.ctx.beginPath();
        this.ctx.moveTo(p.x, p.y);
        this.ctx.lineTo(this.mouse.x, this.mouse.y);
        this.ctx.strokeStyle = `rgba(0, 170, 0, ${0.4 * (1 - distMouse / maxDistance)})`;
        this.ctx.stroke();
      }

      for (let j = i + 1; j < this.particles.length; j++) {
        let p2 = this.particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxDistance) {
          this.ctx.beginPath();
          this.ctx.moveTo(p.x, p.y);
          this.ctx.lineTo(p2.x, p2.y);
          this.ctx.strokeStyle = `rgba(0, 170, 0, ${0.2 * (1 - dist / maxDistance)})`;
          this.ctx.stroke();
        }
      }
    }
  }
}
