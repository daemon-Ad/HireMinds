import { Component, HostListener, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../../core/auth/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  activeTab = signal<'login' | 'register'>('login');
  loading = signal(false);
  error = signal('');

  // Login form
  loginEmail = '';
  loginPassword = '';

  // Register form
  regUsername = '';
  regEmail = '';
  regPassword = '';

  constructor(private auth: AuthService, private router: Router) {
    if (this.auth.isLoggedIn()) {
      this.router.navigate(['/dashboard']);
    }
  }

  setTab(tab: 'login' | 'register') {
    this.activeTab.set(tab);
    this.error.set('');
  }

  @HostListener('window:keydown.escape', ['$event'])
  onEscape() {
    this.router.navigate(['/about']);
  }

  onLogin() {
    if (!this.loginEmail || !this.loginPassword) return;
    this.loading.set(true);
    this.error.set('');

    this.auth.login(this.loginEmail, this.loginPassword).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: (err) => {
        this.error.set(err.error?.detail || 'Login failed. Check your credentials.');
        this.loading.set(false);
      }
    });
  }

  onRegister() {
    if (!this.regUsername || !this.regEmail || !this.regPassword) return;
    this.loading.set(true);
    this.error.set('');

    this.auth.register({ username: this.regUsername, email: this.regEmail, password: this.regPassword }).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: (err) => {
        this.error.set(err.error?.detail || 'Registration failed. Try a different email.');
        this.loading.set(false);
      }
    });
  }
}
