"""
GAD-7 Generalized Anxiety Disorder Assessment.
7-item scale, same 0-3 response format as PHQ-9.
"""
import json
from modules.db.connection import get_connection, placeholder

GAD7_QUESTIONS = [
    "1️⃣ Feeling nervous, anxious, or on edge?",
    "2️⃣ Not being able to stop or control worrying?",
    "3️⃣ Worrying too much about different things?",
    "4️⃣ Trouble relaxing?",
    "5️⃣ Being so restless that it is hard to sit still?",
    "6️⃣ Becoming easily annoyed or irritable?",
    "7️⃣ Feeling afraid as if something awful might happen?",
]

RESPONSE_OPTIONS = (
    "Over the last 2 weeks, how often have you been bothered by this problem?\n\n"
    "0 - Not at all\n"
    "1 - Several days\n"
    "2 - More than half the days\n"
    "3 - Nearly every day\n\n"
    "Reply with 0, 1, 2, or 3."
)

GAD7_LEVELS = [
    (0,  4,  "Minimal Anxiety",   "🟢"),
    (5,  9,  "Mild Anxiety",      "🟡"),
    (10, 14, "Moderate Anxiety",  "🟠"),
    (15, 21, "Severe Anxiety",    "🔴"),
]

GAD7_INSIGHTS = {
    "Minimal Anxiety":   "Your anxiety levels appear minimal. Keep up your healthy habits! 🌟",
    "Mild Anxiety":      "You're experiencing some anxiety. Mindfulness and breathing exercises can help.",
    "Moderate Anxiety":  "Moderate anxiety can be challenging. CBT techniques may significantly help. Consider speaking to a professional.",
    "Severe Anxiety":    "Your responses suggest severe anxiety. Please reach out to a mental health professional soon. I'm here to support you in the meantime.",
}

def classify_gad7(score: int) -> tuple:
    for lo, hi, level, emoji in GAD7_LEVELS:
        if lo <= score <= hi:
            return level, emoji
    return "Severe Anxiety", "🔴"

def save_gad7_result(user_id: int, answers: list) -> dict:
    score = sum(answers)
    level, emoji = classify_gad7(score)
    ph = placeholder()
    with get_connection() as conn:
        conn.cursor().execute(
            f"""INSERT INTO gad7_results (user_id, score, level, answers)
                VALUES ({ph}, {ph}, {ph}, {ph})""",
            (user_id, score, level, json.dumps(answers)),
        )
    return {"score": score, "level": level, "emoji": emoji,
            "insight": GAD7_INSIGHTS[level]}

def get_gad7_history(user_id: int, limit: int = 5) -> list:
    ph = placeholder()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""SELECT score, level, taken_at FROM gad7_results
                WHERE user_id = {ph} ORDER BY taken_at DESC LIMIT {ph}""",
            (user_id, limit),
        )
        return [{"score": r[0], "level": r[1], "taken_at": str(r[2])}
                for r in cur.fetchall()]