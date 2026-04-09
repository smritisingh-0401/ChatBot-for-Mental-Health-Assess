
import logging
from datetime import datetime, date
from modules.db.connection import get_connection, placeholder
from modules.biomarkers.sentiment import analyze_sentiment

logger = logging.getLogger(__name__)

class BiomarkerTracker:
    """One tracker per user session, stored in context.user_data."""

    def __init__(self):
        self.message_lengths = []
        self.sentiments = []
        self.timestamps = []

    def record_message(self, text: str):
        self.message_lengths.append(len(text))
        self.sentiments.append(analyze_sentiment(text))
        self.timestamps.append(datetime.utcnow())

    @property
    def avg_message_length(self) -> float:
        return sum(self.message_lengths) / len(self.message_lengths) if self.message_lengths else 0.0

    @property
    def avg_sentiment(self) -> float:
        return sum(self.sentiments) / len(self.sentiments) if self.sentiments else 0.0

    @property
    def avg_response_delay(self) -> float:
        if len(self.timestamps) < 2:
            return 0.0
        delays = [(self.timestamps[i] - self.timestamps[i-1]).total_seconds()
                  for i in range(1, len(self.timestamps))]
        return sum(delays) / len(delays)

    def persist(self, user_id: int):
        if not self.message_lengths:
            return
        ph = placeholder()
        try:
            with get_connection() as conn:
                conn.cursor().execute(
                    f"""INSERT INTO biomarker_logs
                        (user_id, session_date, avg_msg_length, msg_count, avg_sentiment, response_delay_avg)
                        VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})""",
                    (
                        user_id,
                        str(date.today()),
                        round(self.avg_message_length, 2),
                        len(self.message_lengths),
                        round(self.avg_sentiment, 4),
                        round(self.avg_response_delay, 2),
                    ),
                )
        except Exception as e:
            logger.error(f"Failed to persist biomarkers: {e}")

def get_biomarker_trend(user_id: int, days: int = 14) -> list:
    ph = placeholder()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""SELECT session_date, avg_sentiment, avg_msg_length, msg_count
                FROM biomarker_logs
                WHERE user_id = {ph}
                  AND session_date >= date('now', '-{days} days')
                ORDER BY session_date ASC""",
            (user_id,),
        )
        return [{"date": str(r[0]), "sentiment": r[1],
                 "avg_msg_length": r[2], "msg_count": r[3]}
                for r in cur.fetchall()]

def build_biomarker_insight(trend: list) -> str:
    if len(trend) < 3:
        return "Not enough data yet for biomarker analysis. Keep chatting!"
    sentiments = [t["sentiment"] for t in trend if t["sentiment"] is not None]
    if not sentiments:
        return "No sentiment data available yet."
    recent_avg  = sum(sentiments[-3:]) / 3
    earlier_avg = sum(sentiments[:-3]) / max(len(sentiments[:-3]), 1)
    if recent_avg < earlier_avg - 0.15:
        signal = "Your recent messages show a declining emotional tone. Consider trying /mood or /cbt."
    elif recent_avg > earlier_avg + 0.15:
        signal = "Your emotional tone has been improving recently! Keep it up!"
    else:
        signal = "Your emotional tone has been relatively stable."
    overall = sum(sentiments) / len(sentiments)
    direction = "positive" if overall > 0 else "negative"
    return (
        f"Digital Biomarker Summary (last {len(trend)} days)\n\n"
        f"Average sentiment: {overall:.2f} ({direction})\n\n"
        f"{signal}"
    )