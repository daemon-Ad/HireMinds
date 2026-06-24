import { Component, ElementRef, ViewChild, AfterViewInit, OnDestroy, HostListener } from '@angular/core';

@Component({
  selector: 'app-confetti-burst',
  standalone: true,
  template: `
    <div class="animation-container">
      <h2>Confetti Burst</h2>
      <p class="text-muted">Click anywhere to explode confetti.</p>
      <canvas #canvas (click)="onClick($event)"></canvas>
    </div>
  `,
  styles: [`
    .animation-container { display: flex; flex-direction: column; height: 100%; padding: 1rem; }
    canvas { flex: 1; width: 100%; background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius-lg); margin-top: 1rem; cursor: crosshair; }
  `]
})
export class ConfettiBurstComponent implements AfterViewInit, OnDestroy {
  @ViewChild('canvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  private ctx!: CanvasRenderingContext2D;
  private animationFrameId: number = 0;
  private confetti: any[] = [];
  private colors = ['#00aa00', '#10b981', '#ffffff', '#333333'];

  ngAfterViewInit() {
    this.initCanvas();
    this.animate();
  }
  ngOnDestroy() { cancelAnimationFrame(this.animationFrameId); }
  @HostListener('window:resize') onResize() { this.initCanvas(); }

  onClick(event: MouseEvent) {
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    const mx = event.clientX - rect.left;
    const my = event.clientY - rect.top;

    for (let i = 0; i < 50; i++) {
      this.confetti.push({
        x: mx,
        y: my,
        vx: (Math.random() - 0.5) * 15,
        vy: (Math.random() - 0.5) * 15,
        size: Math.random() * 6 + 4,
        color: this.colors[Math.floor(Math.random() * this.colors.length)],
        angle: Math.random() * Math.PI * 2,
        spin: (Math.random() - 0.5) * 0.2
      });
    }
  }

  private initCanvas() {
    const canvas = this.canvasRef.nativeElement;
    canvas.width = canvas.parentElement?.clientWidth || 800;
    canvas.height = canvas.parentElement?.clientHeight || 600;
    this.ctx = canvas.getContext('2d')!;
  }

  private animate = () => {
    this.animationFrameId = requestAnimationFrame(this.animate);
    const canvas = this.canvasRef.nativeElement;
    this.ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = this.confetti.length - 1; i >= 0; i--) {
      let c = this.confetti[i];
      c.vy += 0.2; // gravity
      c.x += c.vx;
      c.y += c.vy;
      c.angle += c.spin;

      this.ctx.save();
      this.ctx.translate(c.x, c.y);
      this.ctx.rotate(c.angle);
      this.ctx.fillStyle = c.color;
      this.ctx.fillRect(-c.size/2, -c.size/2, c.size, c.size);
      this.ctx.restore();

      if (c.y > canvas.height) {
        this.confetti.splice(i, 1);
      }
    }
  }
}
