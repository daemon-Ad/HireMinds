import json
import logging
from dataclasses import dataclass
from typing import List, Optional

from app.agents.prompts import INTERVIEW_SCHEDULER_SYSTEM, INTERVIEW_SCHEDULER_USER

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


@dataclass
class InterviewEmail:
    email_subject: str
    email_body: str
    proposed_slots: List[str]


class InterviewSchedulerAgent:
    """
    Takes candidate data + JD title + recruiter-provided time slots, calls the LLM
    to generate a personalised interview invitation email, and returns an
    InterviewEmail dataclass with subject and body.
    """

    def run(
        self,
        candidate_name: str,
        jd_title: str,
        recruiter_name: str,
        proposed_slots: List[str],
    ) -> InterviewEmail:
        slots_text = "\n".join(f"- {s}" for s in proposed_slots) if proposed_slots else "To be confirmed"

        prompt = INTERVIEW_SCHEDULER_USER.format(
            candidate_name=candidate_name,
            jd_title=jd_title,
            recruiter_name=recruiter_name,
            proposed_slots=slots_text,
        )

        for attempt in range(1, MAX_RETRIES + 1):
            raw_response = self._call_llm(
                system=INTERVIEW_SCHEDULER_SYSTEM, user=prompt
            )
            try:
                from app.utils.json_validator import parse_llm_response
                data = parse_llm_response(raw_response)
                if data is None:
                    raise ValueError("parse_llm_response returned None")
                return InterviewEmail(
                    email_subject=data.get("email_subject", "Interview Invitation"),
                    email_body=data.get("email_body", ""),
                    proposed_slots=data.get("proposed_slots", proposed_slots),
                )
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                logger.warning(
                    "InterviewSchedulerAgent: attempt %d/%d failed to parse JSON — %s",
                    attempt,
                    MAX_RETRIES,
                    exc,
                )

        logger.error(
            "InterviewSchedulerAgent: all %d attempts exhausted, returning fallback email.",
            MAX_RETRIES,
        )
        return InterviewEmail(
            email_subject="Interview Invitation",
            email_body=(
                f"Dear {candidate_name},\n\n"
                f"We would like to invite you to interview for the {jd_title} role.\n\n"
                f"Proposed slots:\n{slots_text}\n\n"
                f"Best regards,\n{recruiter_name}"
            ),
            proposed_slots=proposed_slots,
        )

    def _call_llm(self, system: str, user: str) -> str:
        """
        Send a prompt to the configured LLM and return the raw response string.
        Replace this method body with your actual LLM client call.
        """
        raise NotImplementedError(
            "InterviewSchedulerAgent._call_llm is not implemented. "
            "Wire up your LLM client (OpenAI, Gemini, etc.) here."
        )
