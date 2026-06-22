import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { JobDescription, JDCreateRequest, JDListResponse } from '../../core/models/models.interface';

@Injectable({ providedIn: 'root' })
export class JdService {
  private readonly API = 'http://localhost:8000/jd';

  constructor(private http: HttpClient) {}

  uploadJD(title: string, rawText: string): Observable<JobDescription> {
    const body: JDCreateRequest = { title, raw_text: rawText };
    return this.http.post<JobDescription>(`${this.API}/upload`, body);
  }

  uploadJDFile(title: string, file: File): Observable<JobDescription> {
    const form = new FormData();
    form.append('title', title);
    form.append('file', file);
    return this.http.post<JobDescription>(`${this.API}/upload`, form);
  }

  // Backend returns { job_descriptions: [...], total: N } — unwrap to plain array
  listJDs(): Observable<JobDescription[]> {
    return this.http.get<JDListResponse>(`${this.API}/`).pipe(
      map(res => res.job_descriptions)
    );
  }

  getJD(jdId: string): Observable<JobDescription> {
    return this.http.get<JobDescription>(`${this.API}/${jdId}`);
  }
}
