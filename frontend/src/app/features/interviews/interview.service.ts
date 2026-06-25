import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Interview, InterviewTriggerRequest } from '../../core/models/models.interface';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class InterviewService {
  private readonly API = `${environment.apiUrl}/interviews`;

  constructor(private http: HttpClient) {}

  sendInterviews(jdId: string, slots: string[], candidateId?: string): Observable<Interview[]> {
    const body: InterviewTriggerRequest = { jd_id: jdId, proposed_slots: slots };
    if (candidateId) body.candidate_id = candidateId;
    return this.http.post<Interview[]>(`${this.API}/send`, body);
  }

  listInterviews(): Observable<Interview[]> {
    return this.http.get<Interview[]>(`${this.API}/`);
  }

  updateInterview(interviewId: string, action: string, newSlots: string[]): Observable<Interview> {
    return this.http.put<Interview>(`${this.API}/${interviewId}`, { action, new_slots: newSlots });
  }
}
