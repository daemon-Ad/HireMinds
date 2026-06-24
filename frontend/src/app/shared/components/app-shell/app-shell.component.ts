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
      <aside class="sidebar" [class.collapsed]="isSidebarCollapsed()">
        <div class="sidebar__logo" routerLink="/about" style="cursor: pointer;">
          <button class="sidebar__toggle" (click)="isSidebarCollapsed.set(!isSidebarCollapsed()); $event.stopPropagation()">
            <span class="material-symbols-rounded">menu</span>
          </button>
          <img src="assets/logo.png" alt="HireMinds Logo" style="height: 1.5em; vertical-align: middle;" *ngIf="!isSidebarCollapsed()">
          <span class="sidebar__logo-text" *ngIf="!isSidebarCollapsed()">HireMinds</span>
        </div>

        <nav class="sidebar__nav">
          <a
            *ngFor="let item of navItems"
            [routerLink]="item.path"
            routerLinkActive="active"
            class="sidebar__nav-item"
          >
            <span class="material-symbols-rounded" [title]="isSidebarCollapsed() ? item.label : ''">{{ item.icon }}</span>
            <span *ngIf="!isSidebarCollapsed()">{{ item.label }}</span>
          </a>
        </nav>

        <div class="sidebar__footer">
          <a routerLink="/api-services" routerLinkActive="active" class="sidebar__nav-item" [title]="isSidebarCollapsed() ? 'API Services' : ''">
            <span class="material-symbols-rounded">api</span>
            <span class="sidebar__nav-text" *ngIf="!isSidebarCollapsed()">API Services</span>
          </a>
          <a routerLink="/about" routerLinkActive="active" class="sidebar__nav-item" [title]="isSidebarCollapsed() ? 'About' : ''">
            <span class="material-symbols-rounded">info</span>
            <span class="sidebar__nav-text" *ngIf="!isSidebarCollapsed()">About</span>
          </a>
          <a href="https://github.com/daemon-Ad/Multi-Agent-AI-Recruitment-Platform" target="_blank" class="sidebar__nav-item" [title]="isSidebarCollapsed() ? 'GitHub' : ''">
            <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub" style="height: 1.3em; filter: invert(1); opacity: 0.7; margin-left: 0.1rem;">
            <span class="sidebar__nav-text" *ngIf="!isSidebarCollapsed()">GitHub</span>
          </a>
          <button class="sidebar__logout" (click)="auth.logout()" [title]="isSidebarCollapsed() ? 'Sign out' : ''">
            <span class="material-symbols-rounded">logout</span>
            <span *ngIf="!isSidebarCollapsed()">Sign out</span>
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
  isSidebarCollapsed = signal(false);

  navItems: NavItem[] = [
    { path: '/dashboard',         label: 'Dashboard',         icon: 'dashboard' },
    { path: '/jd',                label: 'Job Descriptions',  icon: 'description' },
    { path: '/interviews',        label: 'Interviews',        icon: 'calendar_month' },
  ];

  readonly auth = inject(AuthService);
}
