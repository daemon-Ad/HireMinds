import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Interview, InterviewTriggerRequest } from '../../core/models/models.interface';

@Injectable({ providedIn: 'root' })
export class InterviewService {
  private readonly API = 'http://localhost:8000/interviews';

  constructor(private http: HttpClient) {}

  sendInterviews(jdId: string, slots: string[]): Observable<Interview[]> {
    const body: InterviewTriggerRequest = { jd_id: jdId, proposed_slots: slots };
    return this.http.post<Interview[]>(`${this.API}/send`, body);
  }

  listInterviews(): Observable<Interview[]> {
    return this.http.get<Interview[]>(`${this.API}/`);
  }
}
