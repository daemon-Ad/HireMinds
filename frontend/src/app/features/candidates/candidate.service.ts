import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { CandidateMatch } from '../../core/models/models.interface';

@Injectable({ providedIn: 'root' })
export class CandidateService {
  private readonly API = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  uploadCV(file: File): Observable<any> {
    const form = new FormData();
    form.append('file', file);
    return this.http.post(`${this.API}/candidates/upload`, form);
  }

  getRankedCandidates(jdId: string): Observable<CandidateMatch[]> {
    return this.http.get<CandidateMatch[]>(`${this.API}/candidates/${jdId}`);
  }

  getAllCandidates(): Observable<CandidateMatch[]> {
    return this.http.get<CandidateMatch[]>(`${this.API}/candidates/`);
  }

  getCandidateProfile(candidateId: string): Observable<any> {
    return this.http.get<any>(`${this.API}/candidates/profile/${candidateId}`);
  }
}
