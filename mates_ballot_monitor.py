"""
MATES Ballot Monitor — GitHub Actions Edition
----------------------------------------------
Checks the Australian MATES (Subclass 403) ballot status page
and sends an email alert when the ballot becomes ACTIVE.

Credentials are read from environment variables (GitHub Secrets).
State (last known status) is stored in state.json, committed back to the repo.
"""

import urllib.request
import smtplib
import json
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ── Credentials from GitHub Secrets (set via repo Settings → Secrets) ─────────
SENDER_EMAIL    = os.environ["SENDER_EMAIL"]      # your Gmail address
SENDER_PASSWORD = os.environ["SENDER_PASSWORD"]   # 16-char Gmail App Password
RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]   # where to send alerts

# ── Config ─────────────────────────────────────────────────────────────────────
URL        = "https://immi.homeaffairs.gov.au/visas/getting-a-visa/visa-listing/temporary-work-403/mates/ballot-registration/overview"
STATE_FILE = "state.json"   # stored in the repo root, committed after each run


def fetch_page(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_ballot_status(html: str) -> str | None:
    match = re.search(
        r'Ballot registration period.*?\b(ACTIVE|CLOSED|PENDING|EXPIRED)\b',
        html,
        re.IGNORECASE | re.DOTALL

    )
    if match:
        return match.group(1).upper()
    for status in ("ACTIVE", "CLOSED", "PENDING", "EXPIRED"):
        if re.search(rf'\b{status}\b', html):
            return status
    return None


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_status": None, "last_checked": None}


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def send_email(subject: str, body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL

    html_body = f"""
    <html><body>
      <h2 style="color:#007B3B;">🎉 MATES Ballot Alert</h2>
      <p>{body}</p>
      <p><a href="{URL}">👉 Go to the ballot page now</a></p>
      <hr>
      <small>Sent by your MATES Ballot Monitor — {datetime.now().strftime('%d %b %Y %H:%M UTC')}</small>
    </body></html>
    """
    msg.attach(MIMEText(body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())


def main():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] Checking MATES ballot status...")

    state = load_state()

    try:
        html = fetch_page(URL)
    except Exception as e:
        print(f"  ERROR fetching page: {e}")
        raise SystemExit(1)

    status = extract_ballot_status(html)
    print(f"  Ballot status detected: {status}")

    state["last_checked"] = now

    if status is None:
        print("  Could not parse status — page structure may have changed.")
        save_state(state)
        return

    previous = state.get("last_status")

    if status == "ACTIVE" and previous != "ACTIVE":
        print("  🚨 BALLOT IS NOW ACTIVE — sending alert email!")
        send_email(
            subject="🟢 MATES Ballot is NOW OPEN — Register Now!",
            body=(
                f"Good news! The MATES (Subclass 403) ballot status has changed "
                f"from '{previous}' to ACTIVE.\n\n"
                f"Register now at:\n{URL}\n\n"
                f"Don't delay — the registration window may be short!"
            )
        )
        print("  Email sent.")

    elif status != previous and previous is not None:
        print(f"  Status changed: {previous} → {status}")
        send_email(
            subject=f"ℹ️ MATES Ballot status changed to {status}",
            body=(
                f"The MATES ballot status has changed from '{previous}' to '{status}'.\n\n"
                f"Check the page:\n{URL}"
            )
        )
        print("  Notification email sent.")
    
    elif status == "CLOSED":
        print(f"  Status not changed: {previous} → {status}")
        try:
            send_email(
                subject=f"ℹ️ MATES Ballot status NOT changed {status}",
                body=(
                    f"The MATES ballot status has NOT changed from '{previous}' to '{status}'.\n\n"
                    f"Check the page for details:\n{URL}"
                )
            )
            print("  Notification email sent.")
        except Exception as e:
            print(f"  ERROR sending email: {e}") 

    else:
        print(f"  No change (still {status}). Nothing to do.")

    state["last_status"] = status
    save_state(state)
    print("  Done.")


if __name__ == "__main__":
    main()
