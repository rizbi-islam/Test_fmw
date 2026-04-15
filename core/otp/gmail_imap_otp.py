"""
Gmail IMAP OTP Handler.
Reads OTP from Gmail inbox using IMAP.
No paid API needed — uses Gmail's built-in IMAP with App Password.

Setup:
  1. Enable 2-step verification on Gmail
  2. Create App Password: Google Account -> Security -> App Passwords
  3. Enable IMAP in Gmail Settings -> Forwarding and POP/IMAP

Config in config.yaml:
    otp:
      gmail:
        email: "your.test.email@gmail.com"
        app_password: "xxxx xxxx xxxx xxxx"   # 16-char app password
        subject_filter: "Your OTP"             # email subject to search
        otp_regex: "\\b\\d{4,8}\\b"           # regex to extract OTP
        check_interval: 3                      # seconds between checks
"""
import imaplib
import email
import re
import time
from email.header import decode_header
from loguru import logger
from core.otp.base_otp import BaseOTPHandler


class GmailIMAPOTPHandler(BaseOTPHandler):
    """
    Reads OTP from Gmail inbox via IMAP.
    Searches unseen emails matching subject_filter and extracts OTP via regex.
    """

    IMAP_SERVER = "imap.gmail.com"
    IMAP_PORT   = 993

    def __init__(self, config: dict):
        super().__init__(config)
        self.email_addr      = config.get("email", "")
        self.app_password    = config.get("app_password", "")
        self.subject_filter  = config.get("subject_filter", "OTP")
        self.otp_regex       = config.get("otp_regex", r"\b\d{4,8}\b")
        self.check_interval  = int(config.get("check_interval", 3))
        self._mail           = None

    def _connect(self) -> None:
        try:
            self._mail = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
            self._mail.login(self.email_addr, self.app_password)
            self._mail.select("inbox")
            logger.success(f"[GmailIMAPOTP] Connected as {self.email_addr}")
        except Exception as e:
            raise RuntimeError(
                f"[GmailIMAPOTP] Connection failed: {e}\n"
                f"  Ensure App Password is correct and IMAP is enabled in Gmail settings."
            )

    def get_otp(self, timeout: int = 60) -> str:
        """Poll Gmail inbox for OTP email and extract the code."""
        self._connect()
        logger.info(
            f"[GmailIMAPOTP] Polling for email with subject '{self.subject_filter}' "
            f"(timeout={timeout}s, interval={self.check_interval}s)"
        )

        start = time.time()
        while time.time() - start < timeout:
            try:
                otp = self._search_inbox()
                if otp:
                    logger.success(f"[GmailIMAPOTP] OTP extracted: {otp}")
                    return otp
            except Exception as e:
                logger.warning(f"[GmailIMAPOTP] Search error: {e}")
            time.sleep(self.check_interval)

        raise TimeoutError(
            f"[GmailIMAPOTP] No OTP email found within {timeout}s. "
            f"Subject filter: '{self.subject_filter}'"
        )

    def _search_inbox(self) -> str:
        """Search unseen emails matching subject filter and extract OTP."""
        # Re-select to refresh
        self._mail.select("inbox")

        # Search for unseen emails with subject
        search_criteria = f'(UNSEEN SUBJECT "{self.subject_filter}")'
        status, messages = self._mail.search(None, search_criteria)

        if status != "OK" or not messages[0]:
            return ""

        email_ids = messages[0].split()
        # Check most recent first
        for email_id in reversed(email_ids):
            status, msg_data = self._mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            body = self._extract_body(msg)
            otp = self._extract_otp_from_text(body)

            if otp:
                # Mark as read
                self._mail.store(email_id, "+FLAGS", "\\Seen")
                return otp

        return ""

    def _extract_body(self, msg) -> str:
        """Extract plain text body from email message."""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    except Exception:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            except Exception:
                body = str(msg.get_payload())
        return body

    def _extract_otp_from_text(self, text: str) -> str:
        """Extract OTP using configured regex pattern."""
        matches = re.findall(self.otp_regex, text)
        if matches:
            # Return the most likely OTP (first match, or longest if multiple)
            return max(matches, key=len) if len(matches) > 1 else matches[0]
        return ""

    def clear(self) -> None:
        """Disconnect IMAP session."""
        try:
            if self._mail:
                self._mail.close()
                self._mail.logout()
                logger.debug("[GmailIMAPOTP] Disconnected.")
        except Exception:
            pass
