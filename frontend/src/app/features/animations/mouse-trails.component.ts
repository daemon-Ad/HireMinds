import { Component, ElementRef, ViewChild, AfterViewInit, OnDestroy, HostListener } from '@angular/core';

@Component({
  selector: 'app-mouse-trails',
  standalone: true,
  template: `
    <div class="animation-container">
      <h2>Mouse Trails</h2>
      <p class="text-muted">Smooth glowing trails following your cursor.</p>
      <canvas #canvas (mousemove)="onMouseMove($event)"></canvas>
    </div>
  `,
  styles: [`
    .animation-container { display: flex; flex-direction: column; height: 100%; padding: 1rem; }
    canvas { flex: 1; width: 100%; background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius-lg); margin-top: 1rem; cursor: crosshair; }
  `]
})
export class MouseTrailsComponent implements AfterViewInit, OnDestroy {
  @ViewChild('canvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  private ctx!: CanvasRenderingContext2D;
  private animationFrameId: number = 0;
  private points: {x: number, y: number, life: number}[] = [];

  ngAfterViewInit() {
    this.initCanvas();
    this.animate();
  }
  ngOnDestroy() { cancelAnimationFrame(this.animationFrameId); }
  @HostListener('window:resize') onResize() { this.initCanvas(); }

  onMouseMove(event: MouseEvent) {
    const rect = this.canvasRef.nativeElement.getBoundingClientRect();
    this.points.push({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
      life: 1.0
    });
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
}
