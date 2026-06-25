import { Component, ElementRef, ViewChild, AfterViewInit, OnDestroy, HostListener } from '@angular/core';

@Component({
  selector: 'app-magnetic-field',
  standalone: true,
  template: `
    <div class="animation-container">
      <h2>Magnetic Field</h2>
      <p class="text-muted">A grid of indicators pointing towards your cursor.</p>
      <canvas #canvas (mousemove)="onMouseMove($event)"></canvas>
    </div>
  `,
  styles: [`
    .animation-container { display: flex; flex-direction: column; height: 100%; padding: 1rem; }
    canvas { flex: 1; width: 100%; background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius-lg); margin-top: 1rem; }
  `]
})
export class MagneticFieldComponent implements AfterViewInit, OnDestroy {
  @ViewChild('canvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  private ctx!: CanvasRenderingContext2D;
  private animationFrameId: number = 0;
  private mouse = { x: 0, y: 0 };
  private cols = 0;
  private rows = 0;
  private spacing = 30;

  ngAfterViewInit() {
    this.initCanvas();
    this.animate();
  }
  ngOnDestroy() { cancelAnimationFrame(this.animationFrameId); }
  @HostListener('window:resize') onResize() { this.initCanvas(); }

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
    this.cols = Math.floor(canvas.width / this.spacing);
    this.rows = Math.floor(canvas.height / this.spacing);
  }

  private animate = () => {
    this.animationFrameId = requestAnimationFrame(this.animate);
    const canvas = this.canvasRef.nativeElement;
    this.ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let y = 0; y <= this.rows; y++) {
      for (let x = 0; x <= this.cols; x++) {
        const px = x * this.spacing;
        const py = y * this.spacing;

        const dx = this.mouse.x - px;
        const dy = this.mouse.y - py;
        const angle = Math.atan2(dy, dx);
        const dist = Math.sqrt(dx*dx + dy*dy);
        const length = Math.max(5, 15 - dist * 0.02);

        this.ctx.save();
        this.ctx.translate(px, py);
        this.ctx.rotate(angle);
        
        this.ctx.beginPath();
        this.ctx.moveTo(0, 0);
        this.ctx.lineTo(length, 0);
        this.ctx.strokeStyle = `rgba(0, 170, 0, ${1 - Math.min(dist/500, 0.8)})`;
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        this.ctx.restore();
      }
    }
  }
}
