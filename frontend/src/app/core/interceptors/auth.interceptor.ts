import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../auth/auth.service';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.token();

  const handleAuthError = (err: any) => {
    if (err instanceof HttpErrorResponse && err.status === 401) {
      auth.logout();
    }
    return throwError(() => err);
  };

  if (token) {
    const cloned = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
    return next(cloned).pipe(catchError(handleAuthError));
  }

  return next(req).pipe(catchError(handleAuthError));
};
