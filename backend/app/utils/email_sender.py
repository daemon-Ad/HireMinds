"""
SMTP email dispatcher.

Uses Python's built-in smtplib — no extra packages required.

Compatible with any STARTTLS SMTP provider:
  Gmail         — smtp.gmail.com:587        (use an App Password)
  SendGrid      — smtp.sendgrid.net:587     (username="apikey", password=<API key>)
  Outlook/365   — smtp-mail.outlook.com:587

Configure via environment variables (see config.py):
  SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_ENABLED

Design rule: this function NEVER raises. Email failures are logged as
warnings so they never crash the matching/scheduling pipeline.
"""

import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str, from_email: str | None = None) -> bool:
    """
    Send a plain-text email via SMTP (STARTTLS).

    Parameters
    ----------
    to         : recipient email address
    subject    : email subject line
    body       : plain-text body (newlines preserved)
    from_email : override the From: header (recruiter's sender address).
                 Falls back to SMTP_USERNAME if not provided.

    Returns
    -------
    True  — email dispatched successfully
    False — sending skipped (SMTP_ENABLED=false) or failed (error logged)
    """
    from app.config import settings

    if not settings.SMTP_ENABLED:
        logger.info("email_sender: SMTP_ENABLED=false — skipping email to %s", to)
        return False

    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        logger.warning(
            "email_sender: SMTP credentials not configured — skipping email to %s", to
        )
        return False

    # Use recruiter's sender address if provided, otherwise fall back to SMTP_USERNAME
    sender = from_email if from_email else settings.SMTP_USERNAME

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = sender
        msg["To"]      = to

        # Plain-text part — always first so legacy clients get it
        msg.attach(MIMEText(body, "plain", "utf-8"))

        context = ssl.create_default_context()

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(sender, to, msg.as_string())

        logger.info("email_sender: email sent successfully to %s | from=%s | subject=%r", to, sender, subject)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "email_sender: SMTP authentication failed — check SMTP_USERNAME / SMTP_PASSWORD"
        )
    except smtplib.SMTPRecipientsRefused:
        logger.warning("email_sender: recipient refused by server — %s", to)
    except smtplib.SMTPException as exc:
        logger.error("email_sender: SMTP error sending to %s — %s", to, exc)
    except OSError as exc:
        # Covers connection refused, timeout, DNS failures
        logger.error(
            "email_sender: network error connecting to %s:%s — %s",
            settings.SMTP_HOST, settings.SMTP_PORT, exc,
        )

    return False
