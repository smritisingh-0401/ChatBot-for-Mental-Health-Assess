"""
Cognitive Behavioral Therapy (CBT) module.
3 techniques: Thought Record, Behavioural Activation, 4-7-8 Breathing.
"""

CBT_TECHNIQUES = {
    "thought_record": {
        "name": "Thought Record",
        "steps": [
            {"prompt": "What situation triggered your negative feeling?\n\n(e.g., 'My friend did not reply to my message')", "key": "situation"},
            {"prompt": "What emotion(s) did you feel, and how intense? (0-100%)\n\n(e.g., 'Anxious 70%, Sad 50%')", "key": "emotion"},
            {"prompt": "What automatic thought went through your mind?\n\n(e.g., 'They must be angry with me')", "key": "automatic_thought"},
            {"prompt": "What EVIDENCE SUPPORTS this thought? (Facts only, not feelings)", "key": "evidence_for"},
            {"prompt": "What EVIDENCE GOES AGAINST this thought? (Think like a detective)", "key": "evidence_against"},
            {"prompt": "Based on the evidence, what is a MORE BALANCED thought?", "key": "balanced_thought"},
            {
                "prompt": "How do you feel NOW? Rate the same emotion(s) again (0-100%).",
                "key": "emotion_after",
                "final": True,
                "completion_message": (
                    "Thought Record Complete!\n\n"
                    "You have just practised one of the most powerful CBT tools. "
                    "With regular use, this rewires how your brain responds to stress.\n\n"
                    "Tip: Try this whenever you notice a strong negative emotion."
                ),
            },
        ],
    },
    "behavioral_activation": {
        "name": "Behavioural Activation",
        "steps": [
            {"prompt": "What used to give you even a tiny bit of joy or achievement?\n\n(e.g., 'A 10-minute walk', 'Making tea', 'Calling a friend')", "key": "activity"},
            {"prompt": "On a scale of 0-10, what is your current mood?", "key": "mood_before"},
            {
                "prompt": "Your plan is locked in! Do it today, then use /mood to log how it went.\n\nHow confident are you that you will do it? (0-10)",
                "key": "confidence",
                "final": True,
                "completion_message": (
                    "Plan locked in!\n\n"
                    "Behavioural activation works even when motivation is zero — "
                    "action comes before feeling, not after. Use /mood after your activity. 💪"
                ),
            },
        ],
    },
    "breathing": {
        "name": "4-7-8 Breathing",
        "steps": [
            {
                "prompt": (
                    "Round 1 of 4:\n\n"
                    "1. Breathe OUT completely through your mouth\n"
                    "2. Breathe IN through your nose for 4 seconds\n"
                    "3. Hold for 7 seconds\n"
                    "4. Breathe OUT through your mouth for 8 seconds\n\n"
                    "Type 'done' when you have finished round 1."
                ),
                "key": "round1",
            },
            {"prompt": "Well done! Round 2 of 4 — same pattern:\nIN 4 → HOLD 7 → OUT 8\n\nType 'done' when ready.", "key": "round2"},
            {"prompt": "Excellent! Round 3 of 4.\nIN 4 → HOLD 7 → OUT 8\n\nType 'done'.", "key": "round3"},
            {
                "prompt": "Last one! Round 4 of 4.\nIN 4 → HOLD 7 → OUT 8\n\nType 'done'.",
                "key": "round4",
                "final": True,
                "completion_message": (
                    "Breathing exercise complete!\n\n"
                    "Your heart rate and cortisol levels should be dropping right now. "
                    "Use /mood to log how you feel vs before."
                ),
            },
        ],
    },
}

CBT_MENU = (
    "CBT Techniques\n\n"
    "Choose a technique:\n\n"
    "1 - Thought Record (challenge negative thoughts)\n"
    "2 - Behavioural Activation (boost mood with action)\n"
    "3 - 4-7-8 Breathing (calm your nervous system)\n\n"
    "Reply with 1, 2, or 3"
)

TECHNIQUE_MAP = {"1": "thought_record", "2": "behavioral_activation", "3": "breathing"}

def get_cbt_technique(choice: str):
    key = TECHNIQUE_MAP.get(choice)
    return CBT_TECHNIQUES.get(key) if key else None