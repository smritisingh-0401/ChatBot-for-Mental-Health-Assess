"""
Companion mode — social-oriented chatbot features.
Paper 1: 'social-oriented chatbots are significantly more effective
in reducing negative mental health issues than task-oriented programs.'
"""
import random

GREETINGS = [
    "Hey! How is your day going?",
    "Hello! How are things?",
    "Hi there! What is on your mind today?",
    "Good to see you! How have you been feeling lately?",
]

EMPATHY_RESPONSES = {
    "sad": [
        "That sounds really hard. I am glad you are talking about it.",
        "I hear you. It is okay to feel sad — your feelings are valid.",
        "I am sorry you are going through this. Would it help to try a grounding exercise? /mindfulness",
    ],
    "anxious": [
        "Anxiety can feel overwhelming. You do not have to face it alone.",
        "Let us take a breath together. Try /cbt for breathing exercises.",
        "That sounds stressful. The TIPP skill in /dbt can help right now.",
    ],
    "happy": [
        "That is wonderful! What made today good?",
        "I love hearing that! Savour this feeling.",
        "That is great news! Keep noticing these positive moments — they matter.",
    ],
    "neutral": [
        "I am here whenever you want to talk.",
        "Some days are just okay and that is perfectly fine.",
        "What is one small thing that went okay today?",
    ],
}

JOURNAL_PROMPTS = [
    "What is one thing you are grateful for today, even if it is tiny?",
    "What emotion have you felt most strongly today? What triggered it?",
    "What would you tell a close friend who was feeling the way you feel right now?",
    "What is one small step you could take today toward feeling better?",
    "What is something you are looking forward to, even in the distant future?",
    "Describe your current situation using only weather metaphors.",
    "What does your body need most right now — rest, movement, food, or connection?",
]

CHECK_IN_MESSAGE = (
    "Daily Check-in\n\n"
    "How are you feeling today?\n\n"
    "1 - Good\n"
    "2 - Okay\n"
    "3 - Not great\n"
    "4 - Bad\n"
    "5 - Very bad\n\n"
    "Or just tell me about your day in your own words."
)

ANTI_PARASOCIAL_REMINDERS = [
    (
        "While I love our chats, human connections are irreplaceable. "
        "Have you reached out to a friend or family member recently?"
    ),
    (
        "I am here to support you, and I also want you to have other sources of support. "
        "Is there someone you trust that you could reach out to today?"
    ),
]

def get_random_journal_prompt() -> str:
    return random.choice(JOURNAL_PROMPTS)

def get_empathy_response(mood_category: str) -> str:
    responses = EMPATHY_RESPONSES.get(mood_category, EMPATHY_RESPONSES["neutral"])
    return random.choice(responses)

def should_show_anti_parasocial(message_count_today: int) -> bool:
    """Show anti-dependency reminder after every 15th interaction."""
    return message_count_today > 0 and message_count_today % 15 == 0

def get_anti_parasocial_reminder() -> str:
    return random.choice(ANTI_PARASOCIAL_REMINDERS)