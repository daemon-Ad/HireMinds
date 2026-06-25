import logging
from dataclasses import dataclass
from typing import List

from app.agents.prompts import (
    INTERVIEW_SCHEDULER_SYSTEM, INTERVIEW_SCHEDULER_USER,
    INTERVIEW_UPDATE_SYSTEM, INTERVIEW_UPDATE_USER
)
from app.utils.json_validator import parse_llm_response

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


@dataclass
class InterviewEmail:
    email_subject: str
    email_body:    str
    proposed_slots: List[str]


class InterviewSchedulerAgent:
    """
    Generates a personalised interview invitation email via Groq LLaMA.
    This is the only agent that calls an external LLM — all other agents
    are fully local.

    Groq's free tier (llama-3.1-8b-instant) is used because:
    - High rate limits (6000 RPM on free tier)
    - Sufficient quality for email generation
    - Called only on shortlisted candidates (not on every CV upload)
    """

    def run(
        self,
        candidate_name:  str,
        jd_title:        str,
        recruiter_name:  str,
        proposed_slots:  List[str],
    ) -> InterviewEmail:
        slots_text = (
            "\n".join(f"- {s}" for s in proposed_slots)
            if proposed_slots
            else "To be confirmed"
        )

        prompt = INTERVIEW_SCHEDULER_USER.format(
            candidate_name  = candidate_name,
            jd_title        = jd_title,
            recruiter_name  = recruiter_name,
            proposed_slots  = slots_text,
        )

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                raw_response = self._call_llm(
                    system = INTERVIEW_SCHEDULER_SYSTEM,
                    user   = prompt,
                )
            except NotImplementedError:
                raise
            except Exception as exc:
                logger.warning(
                    "InterviewSchedulerAgent: LLM call attempt %d/%d failed — %s",
                    attempt, MAX_RETRIES, exc,
                )
                continue

            data = parse_llm_response(raw_response)
            if data is None:
                logger.warning(
                    "InterviewSchedulerAgent: attempt %d/%d — parse_llm_response returned None",
                    attempt, MAX_RETRIES,
                )
                continue

            return InterviewEmail(
                email_subject  = data.get("email_subject", "Interview Invitation"),
                email_body     = data.get("email_body", ""),
                proposed_slots = data.get("proposed_slots", proposed_slots),
            )

        # All retries exhausted — return a plain fallback email
        logger.error(
            "InterviewSchedulerAgent: all %d attempts exhausted, returning fallback email.",
            MAX_RETRIES,
        )
        return InterviewEmail(
            email_subject  = f"Interview Invitation — {jd_title}",
            email_body     = (
                f"Dear {candidate_name},\n\n"
                f"We would like to invite you to interview for the {jd_title} role.\n\n"
                f"Proposed slots:\n{slots_text}\n\n"
                f"Please confirm your availability at your earliest convenience.\n\n"
                f"Best regards,\n{recruiter_name}"
            ),
            proposed_slots = proposed_slots,
        )

    def update_interview(
        self,
        candidate_name:  str,
        jd_title:        str,
        recruiter_name:  str,
        action:          str,
        proposed_slots:  List[str],
    ) -> InterviewEmail:
        slots_text = (
            "\n".join(f"- {s}" for s in proposed_slots)
            if proposed_slots
            else "None"
        )

        prompt = INTERVIEW_UPDATE_USER.format(
            candidate_name  = candidate_name,
            jd_title        = jd_title,
            recruiter_name  = recruiter_name,
            action          = action,
            proposed_slots  = slots_text,
        )

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                raw_response = self._call_llm(
                    system = INTERVIEW_UPDATE_SYSTEM,
                    user   = prompt,
                )
            except Exception as exc:
                logger.warning(
                    "InterviewSchedulerAgent: update LLM call attempt %d/%d failed — %s",
                    attempt, MAX_RETRIES, exc,
                )
                continue

            data = parse_llm_response(raw_response)
            if data is None:
                continue

            return InterviewEmail(
                email_subject  = data.get("email_subject", f"Interview Update — {jd_title}"),
                email_body     = data.get("email_body", ""),
                proposed_slots = proposed_slots,
            )

        logger.error("InterviewSchedulerAgent: update all %d attempts exhausted, returning fallback.", MAX_RETRIES)
        return InterviewEmail(
            email_subject  = f"Interview Update — {jd_title}",
            email_body     = f"Dear {candidate_name},\n\nThis email is to {action} your interview for the {jd_title} role.\n\nBest regards,\n{recruiter_name}",
            proposed_slots = proposed_slots,
        )

    def _call_llm(self, system: str, user: str) -> str:
        """
        Calls Groq's LLaMA 3.1 8B Instant model.
        Groq client is instantiated here (not at class init) so the import
        only happens when this method is actually called — keeping unit tests
        fast and the agent importable without a GROQ_API_KEY set.
        """
        from groq import Groq
        from app.config import settings

        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model    = settings.GROQ_MODEL,
            messages = [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature = 0.7,
            max_tokens  = 1024,
        )
        return response.choices[0].message.content
