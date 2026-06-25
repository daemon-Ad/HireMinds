import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Status 0 represents a network error or connection refused (server completely offline)
      // Status 502/503 represent bad gateway or service unavailable
      if (error.status === 0 || error.status === 502 || error.status === 503) {
        // Only navigate to offline if we are not already there
        if (router.url !== '/offline') {
          router.navigate(['/offline']);
        }
      }
      return throwError(() => error);
    })
  );
};
