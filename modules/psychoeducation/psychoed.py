
TOPICS = {
    "depression": {
        "title": "Understanding Depression",
        "content": [
            (
                "What is depression?\n\n"
                "Depression is a common but serious medical condition, not a character flaw. "
                "It involves persistent low mood, loss of interest, and a cluster of physical "
                "and cognitive symptoms. It affects approximately 1 in 6 people."
            ),
            (
                "The biology of depression:\n\n"
                "Depression involves changes in brain chemistry (serotonin, dopamine, "
                "norepinephrine), brain structure (smaller hippocampus), and stress hormone "
                "regulation (cortisol). This is why it responds to both psychological AND "
                "biological treatments."
            ),
            (
                "Depression affects 5 domains:\n\n"
                "Thinking: negative thoughts, poor concentration\n"
                "Feelings: sadness, numbness, emptiness\n"
                "Behaviour: withdrawal, reduced activity\n"
                "Physical: sleep, appetite, energy changes\n"
                "Relationships: isolation, conflict\n\n"
                "CBT works by changing the thinking-behaviour cycle."
            ),
            (
                "What helps?\n\n"
                "- Psychotherapy (CBT is most evidence-based)\n"
                "- Medication (for moderate-severe cases)\n"
                "- Exercise (30 min x 3 per week has antidepressant effect)\n"
                "- Sleep hygiene\n"
                "- Social connection\n"
                "- Sunlight exposure\n\n"
                "I can help with CBT techniques via /cbt. For medication, please speak to a doctor."
            ),
        ],
    },
    "anxiety": {
        "title": "Understanding Anxiety",
        "content": [
            (
                "What is anxiety?\n\n"
                "Anxiety is your brain's alarm system — it evolved to protect you from danger. "
                "Modern brains sometimes trigger this alarm for non-threats (traffic, emails, "
                "social situations). GAD (Generalized Anxiety Disorder) is when this alarm "
                "is stuck on."
            ),
            (
                "The anxiety cycle:\n\n"
                "Trigger → Anxious thought → Physical symptoms (racing heart, tension) → "
                "Avoidance → Short-term relief → Anxiety strengthened (repeat)\n\n"
                "Breaking the avoidance cycle is the core of anxiety treatment."
            ),
            (
                "What helps?\n\n"
                "- Exposure therapy (facing feared situations gradually)\n"
                "- Breathing techniques (/cbt then choose Breathing)\n"
                "- Mindfulness (/mindfulness)\n"
                "- Reducing caffeine and alcohol\n"
                "- Regular sleep schedule\n"
                "- Exercise\n\n"
                "DBT's TIPP skill (/dbt) is excellent for acute anxiety."
            ),
        ],
    },
    "sleep": {
        "title": "Sleep and Mental Health",
        "content": [
            (
                "Why sleep matters so much:\n\n"
                "Sleep is when your brain consolidates memories, clears toxic waste, "
                "regulates emotions (sleep deprivation leads to 60% more emotional reactivity), "
                "and resets stress hormone levels.\n\n"
                "Poor sleep is both a symptom AND a cause of depression and anxiety."
            ),
            (
                "Sleep hygiene essentials:\n\n"
                "- Consistency: same bedtime and wake time every day\n"
                "- Screens off: 1 hour before bed (blue light suppresses melatonin)\n"
                "- Cool room: 18-20 degrees Celsius is optimal\n"
                "- Dark room: blackout curtains or sleep mask\n"
                "- No caffeine after 2pm\n"
                "- Wind-down routine: same 20-minute sequence every night"
            ),
        ],
    },
    "stigma": {
        "title": "Mental Health Stigma",
        "content": [
            (
                "Stigma is the biggest barrier to treatment.\n\n"
                "Research shows stigma prevents approximately 70% of people with mental "
                "disorders from seeking help. This is why I exist — to provide a stigma-free "
                "first step.\n\n"
                "Mental illness is:\n"
                "NOT a sign of weakness\n"
                "NOT 'just in your head' in a dismissive sense\n"
                "A real medical condition with real biological components\n"
                "Treatable in the majority of cases"
            ),
        ],
    },
}

PSYCHOED_MENU = (
    "Psychoeducation Library\n\n"
    "What would you like to learn about?\n\n"
    "1 - Depression (what it is and what helps)\n"
    "2 - Anxiety (understanding your alarm system)\n"
    "3 - Sleep (why it is critical for mental health)\n"
    "4 - Stigma (why mental health myths hurt)\n\n"
    "Reply with 1, 2, 3, or 4"
)

TOPIC_MAP = {"1": "depression", "2": "anxiety", "3": "sleep", "4": "stigma"}

def get_topic(choice: str):
    key = TOPIC_MAP.get(choice)
    return TOPICS.get(key) if key else None