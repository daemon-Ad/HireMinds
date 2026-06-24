import { Component, ElementRef, ViewChild, AfterViewInit, OnDestroy, HostListener } from '@angular/core';

@Component({
  selector: 'app-matrix-rain',
  standalone: true,
  template: `
    <div class="animation-container">
      <h2>Matrix Rain</h2>
      <p class="text-muted">Classic digital rain effect mapping characters in brand green.</p>
      <canvas #canvas></canvas>
    </div>
  `,
  styles: [`
    .animation-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      padding: 1rem;
    }
    canvas {
      flex: 1;
      width: 100%;
      background: #000;
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      margin-top: 1rem;
    }
  `]
})
export class MatrixRainComponent implements AfterViewInit, OnDestroy {
  @ViewChild('canvas') canvasRef!: ElementRef<HTMLCanvasElement>;
  
  private ctx!: CanvasRenderingContext2D;
  private animationFrameId: number = 0;
  private columns: number = 0;
  private drops: number[] = [];
  private chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()';

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

  private initCanvas() {
    const canvas = this.canvasRef.nativeElement;
    canvas.width = canvas.parentElement?.clientWidth || 800;
    canvas.height = canvas.parentElement?.clientHeight || 600;
    this.ctx = canvas.getContext('2d')!;
    
    const fontSize = 14;
    this.columns = Math.floor(canvas.width / fontSize);
    this.drops = Array(this.columns).fill(1);
    this.ctx.font = `${fontSize}px monospace`;
  }

  private animate = () => {
    // Slower frame rate for matrix rain
    setTimeout(() => {
      this.animationFrameId = requestAnimationFrame(this.animate);
    }, 50);

    const canvas = this.canvasRef.nativeElement;
    
    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    this.ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    this.ctx.fillStyle = '#10b981';
    
    for (let i = 0; i < this.drops.length; i++) {
      const text = this.chars.charAt(Math.floor(Math.random() * this.chars.length));
      const x = i * 14;
      const y = this.drops[i] * 14;
      
      this.ctx.fillText(text, x, y);
      
      if (y > canvas.height && Math.random() > 0.975) {
        this.drops[i] = 0;
      }
      this.drops[i]++;
    }
  }
}
