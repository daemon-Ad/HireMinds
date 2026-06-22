import { Injectable, signal, computed } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { TokenResponse, RegisterRequest } from '../models/models.interface';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly API = 'http://localhost:8000';
  private readonly TOKEN_KEY = 'recruit_ai_token';

  // Reactive auth state using Signals
  private _token = signal<string | null>(localStorage.getItem(this.TOKEN_KEY));
  readonly isLoggedIn = computed(() => !!this._token());
  readonly token = this._token.asReadonly();

  constructor(private http: HttpClient, private router: Router) {}

  register(data: RegisterRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.API}/auth/register`, data).pipe(
      tap(res => this._saveToken(res.access_token))
    );
  }

  login(email: string, password: string): Observable<TokenResponse> {
    // Backend uses OAuth2PasswordRequestForm — must send as form-data
    const body = new HttpParams()
      .set('username', email)
      .set('password', password);

    return this.http.post<TokenResponse>(`${this.API}/auth/login`, body.toString(), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }).pipe(
      tap(res => this._saveToken(res.access_token))
    );
  }

  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    this._token.set(null);
    this.router.navigate(['/login']);
  }

  private _saveToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
    this._token.set(token);
  }
}
