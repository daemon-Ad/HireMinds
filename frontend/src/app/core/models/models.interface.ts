// Core TypeScript interfaces matching backend schemas exactly

export interface Recruiter {
  recruiter_id: string;
  username: string;
  email: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  username: string; // email passed as username per OAuth2 spec
  password: string;
}

// Matches backend JDResponse exactly (flat fields, not nested)
export interface JobDescription {
  jd_id: string;
  title: string;
  raw_text: string;
  required_skills: string | null;       // JSON string from backend
  min_experience_years: number | null;
  required_education: string | null;
  responsibilities: string | null;      // JSON string from backend
  recruiter_id: string;
  created_at: string;
}

// Helper to parse skills JSON string safely
export function parseSkills(skillsJson: string | null): string[] {
  if (!skillsJson) return [];
  try { return JSON.parse(skillsJson); } catch { return []; }
}

export interface JDListResponse {
  job_descriptions: JobDescription[];
  total: number;
}

export interface JDCreateRequest {
  title: string;
  raw_text: string;
}

export interface JDUpdateRequest {
  title?: string;
}

export interface Candidate {
  candidate_id: string;
  raw_cv_text: string;
  parsed_cv?: ParsedCV;
  recruiter_id: string;
  created_at: string;
}

export interface ParsedCV {
  name: string;
  email: string;
  skills: string[];
  experience_years: number;
  education: string;
  institute?: string;
}

// Matches backend CandidateWithScoreResponse from GET /candidates/{jd_id}
export interface CandidateMatch {
  candidate_id: string;
  name: string;              // candidate's actual name from CV
  email: string;
  phone?: string | null;
  skills?: string | null;          // JSON string
  experience_json?: string | null; // JSON string
  education_json?: string | null;  // JSON string
  raw_cv_text?: string | null;
  created_at: string;
  // Scores are 0–1 fractions from backend — multiply by 100 for display
  overall_score: number;
  skill_score?: number;
  experience_score?: number;
  education_score?: number;
  keyword_score?: number;
  is_shortlisted: boolean;
}

export interface Interview {
  interview_id: string;
  match_id: string;
  recruiter_id: string;
  proposed_slots: string | null;
  status: string;
  email_subject?: string;
  email_body?: string;
  sent_at: string;
  candidate_name?: string;
  jd_title?: string;
}

export interface InterviewTriggerRequest {
  jd_id: string;
  candidate_id?: string;
  proposed_slots: string[];
}

export interface DashboardStats {
  total_jds: number;
  total_candidates: number;
  shortlisted: number;
  interviews_sent: number;
}
