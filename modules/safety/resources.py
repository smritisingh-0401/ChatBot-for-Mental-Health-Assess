"""
Crisis detection module.
Inspired by Paper 1's C-SSRS framework.
Paper finding: 0% of 29 tested apps met full safety criteria.
"""
import re
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class CrisisSeverity:
    NONE     = "none"
    LOW      = "low"
    MODERATE = "moderate"
    HIGH     = "high"
    CRITICAL = "critical"

@dataclass
class CrisisAssessment:
    severity: str
    triggered_patterns: list = field(default_factory=list)
    requires_immediate_escalation: bool = False
    requires_resource_provision: bool = False

# ── Keyword pattern sets (ordered highest to lowest severity) ────────────
# Paper 1: 'censorship-free keyword entry' — we respond with support, not silence.

CRITICAL_PATTERNS = [
    r"i.ve decided.*(die|end|kill|suicide)",
    r"(tonight|today|this week).*(kill|end|die).*(myself|my life)",
    r"i (have|got) (a gun|pills|rope|knife|weapon)",
    r"goodbye (everyone|world|forever)",
    r"suicide (note|letter)",
]

HIGH_PATTERNS = [
    r"i (want|need|am going) to (die|kill myself|end my life|not exist)",
    r"i (don.t|do not) want to (live|be alive|exist) (anymore|any more)",
    r"(life|living) is not worth (it|living)",
    r"no (reason|point) (to|in) (live|living|going on)",
    r"everyone (would be|is) better (off|without) (without me|me)",
    r"i wish i (was|were|am) dead",
]

MODERATE_PATTERNS = [
    r"i (wish|wished) i (wasn.t|was not|weren.t|were not) (here|alive|born)",
    r"i (don.t|do not) (care|matter) (anymore|any more)?",
    r"what.s the point",
    r"(feeling|feel) (hopeless|worthless|like a burden)",
    r"no (hope|future|way out)",
    r"i (hate|can.t stand) myself",
    r"self.harm",
    r"hurt(ing)? myself",
]

LOW_PATTERNS = [
    r"(so|very|extremely|incredibly) (sad|depressed|down|low|alone|lonely)",
    r"can.t (cope|function|go on)",
    r"overwhelmed",
    r"breaking (down|apart)",
    r"(nobody|no one) (cares|understands|loves me)",
]

def _match_patterns(text: str, patterns: list) -> list:
    text_lower = text.lower()
    return [p for p in patterns if re.search(p, text_lower)]

def assess_crisis(text: str) -> CrisisAssessment:
    if not text or len(text.strip()) < 3:
        return CrisisAssessment(severity=CrisisSeverity.NONE)

    if matched := _match_patterns(text, CRITICAL_PATTERNS):
        return CrisisAssessment(
            severity=CrisisSeverity.CRITICAL, triggered_patterns=matched,
            requires_immediate_escalation=True, requires_resource_provision=True,
        )
    if matched := _match_patterns(text, HIGH_PATTERNS):
        return CrisisAssessment(
            severity=CrisisSeverity.HIGH, triggered_patterns=matched,
            requires_immediate_escalation=True, requires_resource_provision=True,
        )
    if matched := _match_patterns(text, MODERATE_PATTERNS):
        return CrisisAssessment(
            severity=CrisisSeverity.MODERATE, triggered_patterns=matched,
            requires_immediate_escalation=False, requires_resource_provision=True,
        )
    if matched := _match_patterns(text, LOW_PATTERNS):
        return CrisisAssessment(
            severity=CrisisSeverity.LOW, triggered_patterns=matched,
            requires_immediate_escalation=False, requires_resource_provision=False,
        )
    return CrisisAssessment(severity=CrisisSeverity.NONE)

def log_crisis_event(user_id: int, trigger_text: str, severity: str):
    from modules.db.connection import get_connection, placeholder
    ph = placeholder()
    try:
        with get_connection() as conn:
            conn.cursor().execute(
                f"""INSERT INTO crisis_events (user_id, trigger_text, severity, resources_sent)
                    VALUES ({ph}, {ph}, {ph}, {ph})""",
                (user_id, trigger_text[:500], severity, 1),
            )
    except Exception as e:
        logger.error(f"Failed to log crisis event: {e}")