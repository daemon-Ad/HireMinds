import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'about',
    loadComponent: () => import('./features/about/about.component').then(m => m.AboutComponent)
  },
  {
    path: '',
    loadComponent: () => import('./shared/components/app-shell/app-shell.component').then(m => m.AppShellComponent),
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent)
      },
      {
        path: 'jd',
        loadComponent: () => import('./features/job-descriptions/job-descriptions.component').then(m => m.JobDescriptionsComponent)
      },
      {
        path: 'candidates/:jd_id',
        loadComponent: () => import('./features/candidates/candidates.component').then(m => m.CandidatesComponent)
      },
      {
        path: 'interviews',
        loadComponent: () => import('./features/interviews/interviews.component').then(m => m.InterviewsComponent)
      }
    ]
  },
  { path: '**', redirectTo: 'dashboard' }
];
