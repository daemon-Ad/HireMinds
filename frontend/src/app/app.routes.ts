import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'about', pathMatch: 'full' },
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
      },
      {
        path: 'candidate/:id',
        loadComponent: () => import('./features/candidates/candidate-profile.component').then(m => m.CandidateProfileComponent)
      },
      {
        path: 'archive/:type',
        loadComponent: () => import('./features/archive/archive.component').then(m => m.ArchiveComponent)
      },
      {
        path: 'animations/matrix',
        loadComponent: () => import('./features/animations/matrix-rain.component').then(m => m.MatrixRainComponent)
      },
      {
        path: 'animations/gravity',
        loadComponent: () => import('./features/animations/gravity-particles.component').then(m => m.GravityParticlesComponent)
      },
      {
        path: 'animations/trails',
        loadComponent: () => import('./features/animations/mouse-trails.component').then(m => m.MouseTrailsComponent)
      },
      {
        path: 'animations/magnetic',
        loadComponent: () => import('./features/animations/magnetic-field.component').then(m => m.MagneticFieldComponent)
      },
      {
        path: 'animations/confetti',
        loadComponent: () => import('./features/animations/confetti-burst.component').then(m => m.ConfettiBurstComponent)
      }

    ]
  },
  { path: '**', redirectTo: 'dashboard' }
];
