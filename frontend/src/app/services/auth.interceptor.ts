import { HttpInterceptorFn, HttpErrorResponse, HttpRequest, HttpHandlerFn } from '@angular/common/http';
import { catchError, switchMap, throwError } from 'rxjs';
import { inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = localStorage.getItem('access_token');
  const http = inject(HttpClient);

  const authReq = token ? req.clone({
    headers: req.headers.set('Authorization', `Bearer ${token}`)
  }) : req;

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        const refresh = localStorage.getItem('refresh_token');
        if (refresh) {
          return http.post('http://localhost:8000/api/auth/refresh/', { refresh }).pipe(
            switchMap((data: any) => {
              localStorage.setItem('access_token', data.access);
              const retryReq = req.clone({
                headers: req.headers.set('Authorization', `Bearer ${data.access}`)
              });
              return next(retryReq);
            }),
            catchError(() => {
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              return throwError(() => error);
            })
          );
        }
        localStorage.removeItem('access_token');
      }
      return throwError(() => error);
    })
  );
};
