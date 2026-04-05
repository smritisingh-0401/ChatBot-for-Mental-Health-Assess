"""
Sentiment analysis using VADER — rule-based, no GPU, works well for chat text.
Paper 2: 'sentiment analysis components analyze emotional tone and psychological states'
"""
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)
_analyzer = SentimentIntensityAnalyzer()

SENTIMENT_CATEGORIES = {
    "very_positive": (0.5,   1.0),
    "positive":      (0.05,  0.5),
    "neutral":       (-0.05, 0.05),
    "negative":      (-0.5,  -0.05),
    "very_negative": (-1.0,  -0.5),
}

def analyze_sentiment(text: str) -> float:
    """Returns VADER compound score: -1.0 (most negative) to +1.0 (most positive)."""
    if not text or len(text.strip()) < 2:
        return 0.0
    try:
        return round(_analyzer.polarity_scores(text)["compound"], 4)
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}")
        return 0.0

def categorize_sentiment(compound: float) -> str:
    for category, (lo, hi) in SENTIMENT_CATEGORIES.items():
        if lo <= compound <= hi:
            return category
    return "neutral"

def get_sentiment_emoji(compound: float) -> str:
    return {
        "very_positive": "😄",
        "positive":      "🙂",
        "neutral":       "😐",
        "negative":      "😟",
        "very_negative": "😢",
    }.get(categorize_sentiment(compound), "😐")