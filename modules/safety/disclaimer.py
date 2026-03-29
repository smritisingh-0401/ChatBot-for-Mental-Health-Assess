"""
Mandatory disclaimer + informed consent gate.
Both papers require explicit disclaimers as a minimal safety standard.
"""
import os
from datetime import datetime
from modules.db.connection import get_connection, placeholder

DISCLAIMER_VERSION = int(os.getenv("BOT_DISCLAIMER_VERSION", "1"))

DISCLAIMER_TEXT = """
⚠️ *Important Notice — Please Read Before Continuing*

This bot is a *wellness support tool*, not a medical device.

✅ What I can do:
- Administer PHQ\-9 and GAD\-7 screening questionnaires
- Share evidence\-based coping strategies \(CBT, DBT, Mindfulness\)
- Provide psychoeducation and emotional check\-ins
- Direct you to professional resources

❌ What I cannot do:
- Diagnose any mental health condition
- Replace a licensed therapist, psychiatrist, or doctor
- Guarantee crisis intervention

🔒 *Privacy:* Your conversations are stored to personalise your experience\. Delete your data anytime with /deletedata\.

📞 *If you are in immediate danger*, please call your local emergency number \(112 in India / 911 in US\) immediately\.

By typing *AGREE*, you confirm you have read and understand the above\.
"""

def has_accepted_disclaimer(user_id: int) -> bool:
    ph = placeholder()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT disclaimer_version FROM users WHERE user_id = {ph}",
            (user_id,),
        )
        row = cur.fetchone()
        if row is None:
            return False
        return (row[0] or 0) >= DISCLAIMER_VERSION

def record_disclaimer_acceptance(user_id: int, username: str = None):
    ph = placeholder()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""INSERT INTO users (user_id, username, disclaimer_version, disclaimer_accepted_at)
                VALUES ({ph}, {ph}, {ph}, {ph})
                ON CONFLICT (user_id) DO UPDATE SET
                    disclaimer_version = excluded.disclaimer_version,
                    disclaimer_accepted_at = excluded.disclaimer_accepted_at""",
            (user_id, username, DISCLAIMER_VERSION, datetime.utcnow()),
        )