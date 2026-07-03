import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../core/auth/auth.service';
import { RecruiterProfile } from '../../core/models/models.interface';

@Component({
  selector: 'app-account-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="settings-page">
      <div class="settings-page__header">
        <h1 class="settings-page__title">
          <span class="material-symbols-rounded">manage_accounts</span>
          Account Settings
        </h1>
        <p class="settings-page__subtitle">Manage your recruiter profile and email preferences.</p>
      </div>

      <!-- Loading skeleton -->
      <div class="settings-card" *ngIf="loading()">
        <div class="skeleton skeleton--line skeleton--wide"></div>
        <div class="skeleton skeleton--line skeleton--medium"></div>
        <div class="skeleton skeleton--line skeleton--narrow"></div>
      </div>

      <!-- Profile Info -->
      <div class="settings-card" *ngIf="!loading() && profile()">
        <div class="settings-card__header">
          <span class="material-symbols-rounded settings-card__icon">person</span>
          <div>
            <h2 class="settings-card__title">Profile</h2>
            <p class="settings-card__desc">Your HireMinds account information.</p>
          </div>
        </div>

        <div class="settings-info-grid">
          <div class="settings-info-item">
            <span class="settings-info-item__label">Username</span>
            <span class="settings-info-item__value">{{ profile()!.username }}</span>
          </div>
          <div class="settings-info-item">
            <span class="settings-info-item__label">Account Email</span>
            <span class="settings-info-item__value">{{ profile()!.email }}</span>
          </div>
        </div>
      </div>

      <!-- Sender Email Settings -->
      <div class="settings-card" *ngIf="!loading() && profile()">
        <div class="settings-card__header">
          <span class="material-symbols-rounded settings-card__icon">mark_email_read</span>
          <div>
            <h2 class="settings-card__title">Interview Sender Email</h2>
            <p class="settings-card__desc">
              Candidates receive interview invitations from this address.
              Changing it takes effect immediately for all future emails.
            </p>
          </div>
        </div>

        <!-- Current value badge -->
        <div class="settings-current" *ngIf="profile()!.sender_email">
          <span class="material-symbols-rounded" style="font-size: 1rem;">check_circle</span>
          Currently sending as: <strong>{{ profile()!.sender_email }}</strong>
        </div>
        <div class="settings-current settings-current--warn" *ngIf="!profile()!.sender_email">
          <span class="material-symbols-rounded" style="font-size: 1rem;">info</span>
          No sender email set — falling back to your account email ({{ profile()!.email }}).
        </div>

        <!-- Edit form -->
        <div class="settings-form">
          <div class="settings-form__field">
            <label for="sender-email-input">Sender Email Address</label>
            <input
              id="sender-email-input"
              type="email"
              [(ngModel)]="newSenderEmail"
              placeholder="hr@yourcompany.com"
              [disabled]="saving()"
              (keydown.enter)="onSave()"
            />
          </div>
          <button
            class="settings-btn settings-btn--primary"
            (click)="onSave()"
            [disabled]="saving() || !newSenderEmail"
          >
            <span class="material-symbols-rounded" *ngIf="!saving()">save</span>
            <span *ngIf="!saving()">Save Changes</span>
            <span *ngIf="saving()" class="loading-dots">Saving</span>
          </button>
        </div>

        <!-- Feedback messages -->
        <div class="settings-feedback settings-feedback--success" *ngIf="successMsg()">
          <span class="material-symbols-rounded">check_circle</span>
          {{ successMsg() }}
        </div>
        <div class="settings-feedback settings-feedback--error" *ngIf="errorMsg()">
          <span class="material-symbols-rounded">error</span>
          {{ errorMsg() }}
        </div>
      </div>
    </div>
  `,
  styles: [`
    .settings-page {
      max-width: 720px;
      margin: 0 auto;
      padding: 2rem 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .settings-page__header { margin-bottom: 0.5rem; }

    .settings-page__title {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      font-size: 1.6rem;
      font-weight: 700;
      color: var(--text-primary);
      margin: 0 0 0.4rem;
      letter-spacing: -0.03em;

      .material-symbols-rounded {
        font-size: 1.8rem;
        color: var(--primary);
      }
    }

    .settings-page__subtitle {
      color: var(--text-muted);
      font-size: 0.9rem;
      margin: 0;
    }

    /* ── Card ──────────────────────────────────────────────── */
    .settings-card {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-xl);
      padding: 1.75rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .settings-card__header {
      display: flex;
      align-items: flex-start;
      gap: 0.9rem;
    }

    .settings-card__icon {
      font-size: 1.4rem;
      color: var(--primary);
      margin-top: 0.1rem;
      flex-shrink: 0;
    }

    .settings-card__title {
      font-size: 1rem;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 0.25rem;
    }

    .settings-card__desc {
      font-size: 0.825rem;
      color: var(--text-muted);
      margin: 0;
      line-height: 1.5;
    }

    /* ── Info Grid ─────────────────────────────────────────── */
    .settings-info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;

      @media (max-width: 520px) { grid-template-columns: 1fr; }
    }

    .settings-info-item {
      background: var(--bg-elevated);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 0.75rem 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.25rem;

      &__label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-muted);
      }

      &__value {
        font-size: 0.9rem;
        color: var(--text-primary);
        font-weight: 500;
      }
    }

    /* ── Current status badge ──────────────────────────────── */
    .settings-current {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.65rem 0.9rem;
      border-radius: var(--radius-md);
      font-size: 0.825rem;
      background: rgba(0, 229, 255, 0.06);
      border: 1px solid rgba(0, 229, 255, 0.18);
      color: var(--text-secondary);

      strong { color: var(--text-primary); }

      &--warn {
        background: rgba(245, 158, 11, 0.07);
        border-color: rgba(245, 158, 11, 0.2);
        color: rgb(245, 158, 11);
      }
    }

    /* ── Form ──────────────────────────────────────────────── */
    .settings-form {
      display: flex;
      gap: 0.75rem;
      align-items: flex-end;

      @media (max-width: 520px) { flex-direction: column; align-items: stretch; }
    }

    .settings-form__field {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 0.4rem;

      label {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-secondary);
      }

      input {
        padding: 0.6rem 0.875rem;
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        color: var(--text-primary);
        font-family: var(--font-sans);
        font-size: 0.875rem;
        outline: none;
        transition: border-color 0.15s, box-shadow 0.15s;
        width: 100%;

        &::placeholder { color: var(--text-muted); }

        &:focus {
          border-color: var(--primary);
          box-shadow: 0 0 0 3px var(--primary-glow);
        }

        &:disabled { opacity: 0.5; cursor: not-allowed; }
      }
    }

    /* ── Button ────────────────────────────────────────────── */
    .settings-btn {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.625rem 1.25rem;
      border: none;
      border-radius: var(--radius-md);
      font-family: var(--font-sans);
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
      white-space: nowrap;

      &--primary {
        background: var(--primary);
        color: #fff;

        &:hover:not(:disabled) {
          background: var(--primary-hover);
          box-shadow: var(--shadow-glow);
        }

        &:disabled { opacity: 0.55; cursor: not-allowed; }
      }

      .material-symbols-rounded { font-size: 1rem; }
    }

    /* ── Feedback ──────────────────────────────────────────── */
    .settings-feedback {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.65rem 0.9rem;
      border-radius: var(--radius-md);
      font-size: 0.825rem;
      animation: fadeIn 0.2s ease;

      .material-symbols-rounded { font-size: 1rem; }

      &--success {
        background: rgba(34, 197, 94, 0.08);
        border: 1px solid rgba(34, 197, 94, 0.2);
        color: rgb(34, 197, 94);
      }

      &--error {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.2);
        color: var(--danger);
      }
    }

    /* ── Note ──────────────────────────────────────────────── */
    .settings-note {
      display: flex;
      align-items: flex-start;
      gap: 0.6rem;
      padding: 1rem 1.1rem;
      background: var(--bg-elevated);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      font-size: 0.8rem;
      color: var(--text-muted);
      line-height: 1.6;

      .material-symbols-rounded {
        font-size: 1.1rem;
        color: var(--primary);
        flex-shrink: 0;
        margin-top: 0.1rem;
      }

      p { margin: 0; }

      strong { color: var(--text-secondary); }

      code {
        background: var(--bg-surface);
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 0.1rem 0.35rem;
        font-size: 0.77rem;
        color: var(--primary);
      }
    }

    /* ── Skeletons ─────────────────────────────────────────── */
    .skeleton {
      height: 1rem;
      background: linear-gradient(90deg, var(--bg-elevated) 25%, var(--bg-surface) 50%, var(--bg-elevated) 75%);
      background-size: 200% 100%;
      animation: shimmer 1.4s infinite;
      border-radius: var(--radius-sm);

      &--wide   { width: 80%; height: 1.4rem; }
      &--medium { width: 55%; }
      &--narrow { width: 35%; }
      &--line   { display: block; }
    }

    @keyframes shimmer {
      0%   { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-4px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .loading-dots::after {
      content: '';
      animation: dots 1.2s steps(3, end) infinite;
    }

    @keyframes dots {
      0%   { content: ''; }
      33%  { content: '.'; }
      66%  { content: '..'; }
      100% { content: '...'; }
    }
  `]
})
export class AccountSettingsComponent implements OnInit {
  private authService = inject(AuthService);

  profile    = signal<RecruiterProfile | null>(null);
  loading    = signal(true);
  saving     = signal(false);
  successMsg = signal('');
  errorMsg   = signal('');

  newSenderEmail = '';

  ngOnInit(): void {
    this.authService.getProfile().subscribe({
      next: (p) => {
        this.profile.set(p);
        this.newSenderEmail = p.sender_email ?? '';
        this.loading.set(false);
      },
      error: () => {
        this.errorMsg.set('Failed to load profile. Please refresh the page.');
        this.loading.set(false);
      }
    });
  }

  onSave(): void {
    if (!this.newSenderEmail || this.saving()) return;

    this.saving.set(true);
    this.successMsg.set('');
    this.errorMsg.set('');

    this.authService.updateSenderEmail(this.newSenderEmail).subscribe({
      next: (updated) => {
        this.profile.set(updated);
        this.saving.set(false);
        this.successMsg.set('Sender email updated successfully. Future interview emails will use this address.');
        setTimeout(() => this.successMsg.set(''), 5000);
      },
      error: (err) => {
        this.saving.set(false);
        this.errorMsg.set(err.error?.detail || 'Failed to update sender email. Please try again.');
        setTimeout(() => this.errorMsg.set(''), 5000);
      }
    });
  }
}
