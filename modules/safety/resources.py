

CRISIS_RESOURCES = {
    "IN": {
        "name": "India",
        "emergency": "112",
        "hotlines": [
            {"name": "iCall (TISS)",           "number": "9152987821",    "hours": "Mon-Sat 8am-10pm"},
            {"name": "Vandrevala Foundation",  "number": "1860-2662-345", "hours": "24/7"},
            {"name": "SNEHI",                  "number": "044-24640050",  "hours": "Mon-Sat 8am-10pm"},
            {"name": "NIMHANS",                "number": "080-46110007",  "hours": "Mon-Sat"},
        ],
        "note": "If in immediate danger, call 112 (India emergency).",
    },
    "US": {
        "name": "United States",
        "emergency": "911",
        "hotlines": [
            {"name": "988 Suicide & Crisis Lifeline", "number": "988",                   "hours": "24/7"},
            {"name": "Crisis Text Line",              "number": "Text HOME to 741741",   "hours": "24/7"},
        ],
        "note": "If in immediate danger, call 911.",
    },
    "GB": {
        "name": "United Kingdom",
        "emergency": "999",
        "hotlines": [
            {"name": "Samaritans",          "number": "116 123",           "hours": "24/7"},
            {"name": "PAPYRUS (under 35)",  "number": "0800 068 4141",     "hours": "Daily 9am-midnight"},
            {"name": "Crisis Text Line",    "number": "Text SHOUT to 85258","hours": "24/7"},
        ],
        "note": "If in immediate danger, call 999.",
    },
    "AU": {
        "name": "Australia",
        "emergency": "000",
        "hotlines": [
            {"name": "Lifeline",     "number": "13 11 14",     "hours": "24/7"},
            {"name": "Beyond Blue",  "number": "1300 22 4636", "hours": "24/7"},
        ],
        "note": "If in immediate danger, call 000.",
    },
    "CA": {
        "name": "Canada",
        "emergency": "911",
        "hotlines": [
            {"name": "Talk Suicide Canada", "number": "1-833-456-4566", "hours": "24/7"},
        ],
        "note": "If in immediate danger, call 911.",
    },
    "DEFAULT": {
        "name": "International",
        "emergency": "Local emergency number",
        "hotlines": [
            {"name": "International Association for Suicide Prevention",
             "number": "https://www.iasp.info/resources/Crisis_Centres/", "hours": "24/7"},
            {"name": "Befrienders Worldwide",
             "number": "https://www.befrienders.org", "hours": "24/7"},
        ],
        "note": "Please call your local emergency number if in immediate danger.",
    },
}


def get_resources(region: str) -> dict:
    return CRISIS_RESOURCES.get(region.upper(), CRISIS_RESOURCES["DEFAULT"])


def format_crisis_response(severity: str, region: str) -> str:
    resources = get_resources(region)

    if severity in ("critical", "high"):
        hotline_text = "\n".join(
            f"{h['name']}: {h['number']} ({h['hours']})"
            for h in resources["hotlines"]
        )
        return (
            f"I hear you, and I am concerned about your safety right now.\n\n"
            f"Please reach out to one of these {resources['name']} crisis lines:\n\n"
            f"{hotline_text}\n\n"
            f"{resources['note']}\n\n"
            f"You are not alone. These counsellors are trained to help and will not judge you.\n\n"
            f"I will be here when you are ready to talk more."
        )

    if severity == "moderate":
        hotline = resources["hotlines"][0] if resources["hotlines"] else None
        hotline_text = f"{hotline['name']}: {hotline['number']}" if hotline else ""
        return (
            f"I am hearing that things are really hard right now, and I am glad you told me.\n\n"
            f"You do not have to go through this alone. If you ever feel like you might hurt "
            f"yourself, please reach out:\n\n"
            f"{hotline_text}\n\n"
            f"Would you like to try a grounding exercise? /mindfulness\n"
            f"Or tell me more about what is going on."
        )

    return ""