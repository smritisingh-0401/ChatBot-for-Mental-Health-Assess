"""DBT skills: TIPP, STOP, DEAR MAN."""

DBT_SKILLS = {
    "tipp": {
        "name": "TIPP — Crisis Survival",
        "content": (
            "TIPP stands for:\n\n"
            "T — Temperature\n"
            "Hold your face in cold water for 30 seconds. This triggers the dive reflex and slows your heart rate.\n\n"
            "I — Intense Exercise\n"
            "Do jumping jacks or run in place for 20 minutes. Burns off excess stress hormones.\n\n"
            "P — Paced Breathing\n"
            "Breathe OUT longer than you breathe in. Try: IN for 4, OUT for 6 counts.\n\n"
            "P — Progressive Muscle Relaxation\n"
            "Tense each muscle group for 5 seconds, then release. Start from toes, work up to face.\n\n"
            "Which skill do you want to try first? Reply: T, I, or P"
        ),
    },
    "stop": {
        "name": "STOP Skill",
        "content": (
            "When you feel overwhelmed and at risk of doing something impulsive, use STOP:\n\n"
            "S — Stop. Freeze. Do not act yet.\n\n"
            "T — Take a step back. Breathe.\n\n"
            "O — Observe. What am I feeling? What triggered this? What are my options?\n\n"
            "P — Proceed mindfully. Do what moves you toward your values.\n\n"
            "Take a moment now. Tell me what situation you are in, and we will apply STOP together."
        ),
    },
    "dear_man": {
        "name": "DEAR MAN — Assertive Communication",
        "content": (
            "DEAR MAN helps you communicate effectively:\n\n"
            "D — Describe the situation factually\n"
            "E — Express how you feel (use 'I feel...')\n"
            "A — Assert what you want or need clearly\n"
            "R — Reinforce — explain why it benefits both of you\n\n"
            "M — Mindful — stay focused on your goal\n"
            "A — Appear confident — voice, posture\n"
            "N — Negotiate — be willing to give and take\n\n"
            "Tell me about a situation where you need to assert yourself, "
            "and I will help you script your DEAR MAN response."
        ),
    },
}

DBT_MENU = (
    "DBT Skills\n\n"
    "1 - TIPP (rapid crisis survival)\n"
    "2 - STOP (prevent impulsive reactions)\n"
    "3 - DEAR MAN (assertive communication)\n\n"
    "Reply with 1, 2, or 3"
)

SKILL_MAP = {"1": "tipp", "2": "stop", "3": "dear_man"}

def get_dbt_skill(choice: str):
    key = SKILL_MAP.get(choice)
    return DBT_SKILLS.get(key) if key else None