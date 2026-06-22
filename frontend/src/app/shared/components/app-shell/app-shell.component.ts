import { Component, signal, inject } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/auth/auth.service';

interface NavItem {
  path: string;
  label: string;
  icon: string;
}

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule],
  template: `
    <div class="shell">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar__logo">
          <span class="sidebar__logo-icon">⚡</span>
          <span class="sidebar__logo-text">RecruitAI</span>
        </div>

        <nav class="sidebar__nav">
          <a
            *ngFor="let item of navItems"
            [routerLink]="item.path"
            routerLinkActive="active"
            class="sidebar__nav-item"
          >
            <span class="material-symbols-rounded">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </a>
        </nav>

        <div class="sidebar__footer">
          <a routerLink="/about" routerLinkActive="active" class="sidebar__nav-item">
            <span class="material-symbols-rounded">info</span>
            <span>About</span>
          </a>
          <button class="sidebar__logout" (click)="auth.logout()">
            <span class="material-symbols-rounded">logout</span>
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      <!-- Main content -->
      <main class="shell__main">
        <router-outlet />
      </main>
    </div>
  `,
  styleUrl: './app-shell.component.scss'
})
export class AppShellComponent {
  navItems: NavItem[] = [
    { path: '/dashboard',   label: 'Dashboard',         icon: 'dashboard' },
    { path: '/jd',          label: 'Job Descriptions',  icon: 'description' },
    { path: '/interviews',  label: 'Interviews',        icon: 'calendar_month' },
  ];

  readonly auth = inject(AuthService);
}
