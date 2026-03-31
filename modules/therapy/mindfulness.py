"""Mindfulness exercises: Grounding, Body Scan, Loving-Kindness."""

MINDFULNESS_EXERCISES = {
    "grounding": {
        "name": "5-4-3-2-1 Grounding",
        "steps": [
            "5 THINGS YOU CAN SEE\nLook around and name 5 things. Take your time.\n\nType them when ready.",
            "4 THINGS YOU CAN TOUCH\nTouch 4 things. Notice the texture.\n\nType them when ready.",
            "3 THINGS YOU CAN HEAR\nListen carefully. What do you hear?\n\nType them when ready.",
            "2 THINGS YOU CAN SMELL\nNotice any scents. Even subtle ones.\n\nType them when ready.",
            "1 THING YOU CAN TASTE\nWhat do you taste right now?\n\nType it when ready.",
        ],
        "completion": (
            "Grounding Complete!\n\n"
            "You have successfully pulled your mind back to the present moment. "
            "Anxiety lives in the future; depression lives in the past. "
            "This moment, right now, is manageable.\n\nHow do you feel? Use /mood to log it."
        ),
    },
    "body_scan": {
        "name": "Body Scan",
        "content": (
            "Find a comfortable position. Close your eyes if you can.\n\n"
            "Feet and Legs: Notice any tension or tingling. Breathe into that area and let it soften.\n\n"
            "Stomach and Chest: Notice your belly rising and falling. If there is tightness, breathe gently.\n\n"
            "Shoulders and Neck: Let your shoulders drop away from your ears.\n\n"
            "Face: Relax your jaw. Unclench your teeth. Soften around your eyes.\n\n"
            "Whole body: Rest in awareness for 3 breaths.\n\n"
            "When you are ready, open your eyes and type 'done'."
        ),
        "is_single_step": True,
    },
    "loving_kindness": {
        "name": "Loving-Kindness Meditation",
        "content": (
            "Place both hands on your heart. Take 3 slow breaths.\n\n"
            "Silently repeat these phrases for yourself:\n\n"
            "May I be happy\n"
            "May I be healthy\n"
            "May I be safe\n"
            "May I live with ease\n\n"
            "Now think of someone you love. Send them the same wishes.\n\n"
            "Finally, if you are able, extend this to someone you find difficult.\n\n"
            "Take 3 more deep breaths, then type 'done'."
        ),
        "is_single_step": True,
    },
}

MINDFULNESS_MENU = (
    "Mindfulness Exercises\n\n"
    "1 - 5-4-3-2-1 Grounding (for anxiety/panic)\n"
    "2 - Body Scan (for stress and tension)\n"
    "3 - Loving-Kindness (for self-compassion)\n\n"
    "Reply with 1, 2, or 3"
)

EXERCISE_MAP = {"1": "grounding", "2": "body_scan", "3": "loving_kindness"}

def get_mindfulness_exercise(choice: str):
    key = EXERCISE_MAP.get(choice)
    return MINDFULNESS_EXERCISES.get(key) if key else None