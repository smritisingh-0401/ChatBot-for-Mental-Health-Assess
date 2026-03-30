"""
Daily mood check-in with digital biomarker enrichment.
Paper 2: continuous monitoring and digital biomarkers.
"""
from modules.db.connection import get_connection, placeholder

MOOD_EMOJIS = {
    1: "😭", 2: "😢", 3: "😟", 4: "😕", 5: "😐",
    6: "🙂", 7: "😊", 8: "😄", 9: "😁", 10: "🤩"
}

MOOD_PROMPT = (
    "📊 Daily Mood Check-in\n\n"
    "How are you feeling today? Reply with a number from 1 to 10:\n\n"
    "😭 1 = Terrible  |  😐 5 = Neutral  |  🤩 10 = Amazing\n\n"
    "You can also add a note after the number (e.g., '7 Had a good day')"
)

def log_mood(user_id: int, mood_score: int, note: str = None,
             sentiment_compound: float = None) -> dict:
    if not 1 <= mood_score <= 10:
        raise ValueError("mood_score must be between 1 and 10")
    ph = placeholder()
    with get_connection() as conn:
        conn.cursor().execute(
            f"""INSERT INTO mood_logs (user_id, mood_score, note, sentiment_compound)
                VALUES ({ph}, {ph}, {ph}, {ph})""",
            (user_id, mood_score, note, sentiment_compound),
        )
    return {"score": mood_score, "emoji": MOOD_EMOJIS[mood_score]}

def get_mood_trend(user_id: int, days: int = 7) -> list:
    ph = placeholder()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""SELECT mood_score, sentiment_compound, logged_at
                FROM mood_logs
                WHERE user_id = {ph}
                  AND logged_at >= datetime('now', '-{days} days')
                ORDER BY logged_at ASC""",
            (user_id,),
        )
        return [{"score": r[0], "sentiment": r[1], "date": str(r[2])[:10]}
                for r in cur.fetchall()]

def build_trend_summary(trend: list) -> str:
    if not trend:
        return "No mood data yet. Use /mood to log your first check-in!"
    scores = [t["score"] for t in trend]
    avg = sum(scores) / len(scores)
    if scores[-1] > scores[0]:
        direction = "📈 improving"
    elif scores[-1] < scores[0]:
        direction = "📉 declining"
    else:
        direction = "➡️ stable"
    return (
        f"📊 Your {len(trend)}-day mood trend\n"
        f"Average: {avg:.1f}/10  |  Trend: {direction}\n"
        f"Latest: {MOOD_EMOJIS.get(scores[-1], '')} {scores[-1]}/10"
    )