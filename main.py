# ============================================================
# main.py  —  MindCare Bot  (v2 upgrade, Days 1-6)
# ============================================================

import nest_asyncio
nest_asyncio.apply()

import sys
import asyncio
import os
import logging
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ── Existing project imports ───────────────────────────────────────────────
from database import init_database, save_user, save_conversation, save_assessment, get_user_assessments
from depression_detector import DepressionDetector, PHQ9_QUESTIONS

# ── v2 imports ─────────────────────────────────────────────────────────────
from modules.safety.disclaimer import (
    DISCLAIMER_TEXT, has_accepted_disclaimer, record_disclaimer_acceptance
)
from modules.db.schema import run_migrations
from modules.assessment.gad7 import GAD7_QUESTIONS, RESPONSE_OPTIONS, save_gad7_result
from modules.assessment.mood_tracker import (
    MOOD_PROMPT, log_mood, get_mood_trend, build_trend_summary
)
from modules.therapy.cbt import CBT_MENU, get_cbt_technique
from modules.therapy.dbt import DBT_MENU, get_dbt_skill
from modules.therapy.mindfulness import MINDFULNESS_MENU, get_mindfulness_exercise
from modules.psychoeducation.psychoed import PSYCHOED_MENU, get_topic
from modules.companion.companion import (
    CHECK_IN_MESSAGE, get_random_journal_prompt,
    get_empathy_response, should_show_anti_parasocial, get_anti_parasocial_reminder
)
from modules.safety.crisis_detector import assess_crisis, CrisisSeverity, log_crisis_event
from modules.safety.resources import format_crisis_response
from modules.biomarkers.tracker import BiomarkerTracker, build_biomarker_insight, get_biomarker_trend

# ── Windows event loop fix ─────────────────────────────────────────────────
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DEFAULT_REGION = os.getenv('DEFAULT_CRISIS_REGION', 'IN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── Conversation states ────────────────────────────────────────────────────
(
    START, MENU, ASSESSMENT_START, ASKING_QUESTION,
    ASSESSMENT_RESULT, SUPPORT, END
) = range(7)

THERAPY_SELECT, THERAPY_STEP   = range(2)
PSYCHOED_SELECT, PSYCHOED_PAGE = range(2)

user_assessments = {}
detector = DepressionDetector()


# ============================================================
# Original Handlers (PHQ-9) — UNCHANGED
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Start command from user: {user.id}")
    if not has_accepted_disclaimer(user.id):
        await update.message.reply_text(DISCLAIMER_TEXT)
        context.user_data["awaiting_disclaimer"] = True
        return MENU
    save_user(user.id, user.username, user.first_name, user.last_name)
    welcome_message = (
        f"👋 Welcome to MindCare Bot, {user.first_name}!\n\n"
        "This chatbot can:\n"
        "✅ Depression screening (PHQ-9)\n"
        "✅ Anxiety screening (GAD-7)\n"
        "✅ CBT, DBT and Mindfulness tools\n"
        "✅ Psychoeducation library\n"
        "✅ Daily mood tracking\n\n"
        "⚠️ NOT a substitute for professional medical advice.\n\n"
        "What would you like to do?"
    )
    keyboard = [
        [InlineKeyboardButton("📋 Start PHQ-9 Assessment", callback_data='start_assessment')],
        [InlineKeyboardButton("📊 View Previous Results",   callback_data='view_results')],
        [InlineKeyboardButton("❓ Help & Resources",         callback_data='resources')],
        [InlineKeyboardButton("🚪 Exit",                    callback_data='exit')]
    ]
    await update.message.reply_text(welcome_message, reply_markup=InlineKeyboardMarkup(keyboard))
    return MENU


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📋 Start PHQ-9 Assessment", callback_data='start_assessment')],
        [InlineKeyboardButton("📊 View Previous Results",   callback_data='view_results')],
        [InlineKeyboardButton("❓ Help & Resources",         callback_data='resources')],
        [InlineKeyboardButton("🚪 Exit",                    callback_data='exit')]
    ]
    await query.edit_message_text(
        "📋 MindCare Main Menu\n\nWhat would you like to do today?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MENU


async def start_assessment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    user_assessments[user_id] = {'current_question': 0, 'answers': [], 'user_id': user_id}
    instruction = (
        "🧠 PHQ-9 Depression Screening\n\n"
        "9 questions about the past 2 weeks.\n\n"
        "• 😊 Not at all (0)\n• 😔 Several days (1)\n"
        "• 😞 More than half (2)\n• 😢 Nearly every day (3)\n\nLet's begin! 👇"
    )
    await query.edit_message_text(instruction)
    await asyncio.sleep(0.5)
    await ask_phq9_question(update, context)
    return ASKING_QUESTION


async def ask_phq9_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_assessments:
        user_assessments[user_id] = {'current_question': 0, 'answers': []}
    assessment   = user_assessments[user_id]
    question_idx = assessment['current_question']
    if question_idx >= len(PHQ9_QUESTIONS):
        await show_assessment_result(update, context)
        return ASSESSMENT_RESULT
    question = PHQ9_QUESTIONS[question_idx]
    keyboard = [
        [InlineKeyboardButton("😊 Not at all",       callback_data='answer_0')],
        [InlineKeyboardButton("😔 Several days",     callback_data='answer_1')],
        [InlineKeyboardButton("😞 More than half",   callback_data='answer_2')],
        [InlineKeyboardButton("😢 Nearly every day", callback_data='answer_3')]
    ]
    message_text = f"Question {question_idx + 1}/9\n\n{question}"
    query = update.callback_query
    if query:
        try:
            await query.edit_message_text(message_text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            await query.message.reply_text(message_text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(message_text, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    if user_id not in user_assessments:
        await query.edit_message_text("Session expired. Please start again with /start")
        return MENU
    try:
        answer_value = int(query.data.split('_')[1])
    except (IndexError, ValueError):
        await query.edit_message_text("Invalid answer. Please try again.")
        return ASKING_QUESTION
    user_assessments[user_id]['answers'].append(answer_value)
    user_assessments[user_id]['current_question'] += 1
    if user_assessments[user_id]['current_question'] < len(PHQ9_QUESTIONS):
        await ask_phq9_question(update, context)
        return ASKING_QUESTION
    else:
        await show_assessment_result(update, context)
        return ASSESSMENT_RESULT


async def show_assessment_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    user_id = update.effective_user.id
    if user_id not in user_assessments:
        await query.edit_message_text("Session expired.")
        return MENU
    answers    = user_assessments[user_id]['answers']
    phq9_score = sum(answers)
    result     = detector.classify_score(phq9_score)
    severity   = result['severity']
    save_assessment(user_id, phq9_score, severity)
    result_message = (
        f"📊 PHQ-9 Results\n\nScore: {phq9_score}/27\nSeverity: {severity}\n\n"
        f"{result.get('message', '')}\n\n{result.get('recommendations', '')}\n\n"
        f"⚠️ Screening tool only — not a diagnosis."
    )
    keyboard = [
        [InlineKeyboardButton("📋 Take Again",   callback_data='start_assessment')],
        [InlineKeyboardButton("💚 Self-Care",     callback_data='self_care')],
        [InlineKeyboardButton("↩️ Main Menu",     callback_data='menu')],
    ]
    if query:
        await query.edit_message_text(result_message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(result_message, reply_markup=InlineKeyboardMarkup(keyboard))
    del user_assessments[user_id]
    return MENU


async def show_resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg = (
        "❓ Help & Resources\n\n"
        "🆘 India Crisis Lines:\n"
        "• iCall (TISS): 9152987821\n"
        "• Vandrevala: 1860-2662-345\n"
        "• NIMHANS: 080-46110007\n"
        "• Emergency: 112\n\n"
        "New commands:\n"
        "/gad7 /cbt /dbt /mindfulness /learn /mood /trend /journal\n"
        "/setregion — change your crisis resource region"
    )
    keyboard = [
        [InlineKeyboardButton("💚 Self-Care Tips", callback_data='self_care')],
        [InlineKeyboardButton("↩️ Main Menu",      callback_data='menu')],
    ]
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))


async def show_self_care(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg = (
        "💚 Self-Care Tips\n\n"
        "• Sleep 7-9 hours\n• Exercise 30 min/day\n"
        "• Try /mindfulness or /cbt\n• Journal with /journal\n"
        "• Connect with loved ones\n\n"
        "iCall: 9152987821 (Mon-Sat 8am-10pm)"
    )
    keyboard = [[InlineKeyboardButton("↩️ Main Menu", callback_data='menu')]]
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))


async def view_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    assessments = get_user_assessments(user_id)
    if not assessments:
        message = "📊 No previous assessments found."
    else:
        message = "📊 Assessment History:\n\n"
        for i, (score, severity, date) in enumerate(assessments[:5], 1):
            message += f"{i}. {date}\n   Score: {score}/27 - {severity}\n\n"
    keyboard = [
        [InlineKeyboardButton("↩️ Main Menu", callback_data='menu')],
        [InlineKeyboardButton("🚪 Exit",      callback_data='exit')]
    ]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        if query.data == 'menu':
            await show_menu(update, context)
        elif query.data == 'start_assessment':
            await start_assessment(update, context)
        elif query.data == 'resources':
            await show_resources(update, context)
        elif query.data == 'self_care':
            await show_self_care(update, context)
        elif query.data == 'view_results':
            await view_results(update, context)
        elif query.data.startswith('answer_'):
            await handle_answer(update, context)
        elif query.data == 'exit':
            await query.edit_message_text("👋 Thank you for using MindCare Bot. Take care!")
    except Exception as e:
        logger.error(f"Error in button callback: {e}")
        await query.answer("An error occurred. Please try again.")


# ============================================================
# v2 — Disclaimer (Day 2)
# ============================================================

async def handle_disclaimer_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_disclaimer"):
        return
    if update.message.text.strip().upper() == "AGREE":
        user = update.effective_user
        record_disclaimer_acceptance(user.id, user.username)
        save_user(user.id, user.username, user.first_name, user.last_name)
        context.user_data.pop("awaiting_disclaimer", None)
        keyboard = [
            [InlineKeyboardButton("📋 Start PHQ-9 Assessment", callback_data='start_assessment')],
            [InlineKeyboardButton("📊 View Previous Results",   callback_data='view_results')],
            [InlineKeyboardButton("❓ Help & Resources",         callback_data='resources')],
            [InlineKeyboardButton("🚪 Exit",                    callback_data='exit')]
        ]
        await update.message.reply_text(
            "✅ Thank you! You're all set.\n\nWhat would you like to do?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await update.message.reply_text("Please type AGREE to continue, or /start to restart.")


# ============================================================
# v2 — GAD-7 (Day 3)
# ============================================================

async def gad7_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gad7_answers"] = []
    await update.message.reply_text(
        "📋 GAD-7 Anxiety Screening\n\nI'll ask you 7 quick questions.\n\n"
        + GAD7_QUESTIONS[0] + "\n\n" + RESPONSE_OPTIONS
    )
    return 0


async def gad7_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text not in ["0", "1", "2", "3"]:
        await update.message.reply_text("Please reply with 0, 1, 2, or 3.")
        return len(context.user_data.get("gad7_answers", []))
    context.user_data["gad7_answers"].append(int(text))
    step = len(context.user_data["gad7_answers"])
    if step < 7:
        await update.message.reply_text(GAD7_QUESTIONS[step] + "\n\n" + RESPONSE_OPTIONS)
        return step
    result = save_gad7_result(update.effective_user.id, context.user_data["gad7_answers"])
    await update.message.reply_text(
        f"✅ GAD-7 Complete!\n\nScore: {result['score']}/21 {result['emoji']}\n"
        f"Level: {result['level']}\n\n{result['insight']}\n\n"
        f"Try /cbt or /mindfulness for anxiety management."
    )
    context.user_data.pop("gad7_answers", None)
    return ConversationHandler.END


gad7_handler = ConversationHandler(
    entry_points=[CommandHandler("gad7", gad7_start)],
    states={i: [MessageHandler(filters.TEXT & ~filters.COMMAND, gad7_answer)] for i in range(7)},
    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
)


# ============================================================
# v2 — Mood Tracking (Day 3)
# ============================================================

async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(MOOD_PROMPT)
    context.user_data["awaiting_mood"] = True


async def handle_mood_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_mood"):
        return
    parts = update.message.text.strip().split(maxsplit=1)
    try:
        score = int(parts[0])
        note  = parts[1] if len(parts) > 1 else None
        sentiment = None
        if note:
            try:
                from modules.biomarkers.sentiment import analyze_sentiment
                sentiment = analyze_sentiment(note)
            except ImportError:
                pass
        result = log_mood(update.effective_user.id, score, note, sentiment)
        context.user_data.pop("awaiting_mood", None)
        await update.message.reply_text(
            f"Logged! {result['emoji']} {result['score']}/10\n\nUse /trend to see your mood over time."
        )
    except (ValueError, IndexError):
        await update.message.reply_text("Please send a number 1-10, e.g. '7' or '7 Feeling good today'")


async def trend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trend   = get_mood_trend(update.effective_user.id, days=7)
    summary = build_trend_summary(trend)
    await update.message.reply_text(summary)


# ============================================================
# v2 — Therapy: CBT / DBT / Mindfulness (Day 4)
# ============================================================

async def cbt_command(update, context):
    await update.message.reply_text(CBT_MENU)
    context.user_data.update({"therapy_mode": "cbt", "therapy_step": 0, "therapy_data": {}})
    return THERAPY_SELECT

async def dbt_command(update, context):
    await update.message.reply_text(DBT_MENU)
    context.user_data["therapy_mode"] = "dbt"
    return THERAPY_SELECT

async def mindfulness_command(update, context):
    await update.message.reply_text(MINDFULNESS_MENU)
    context.user_data["therapy_mode"] = "mindfulness"
    return THERAPY_SELECT

async def therapy_select(update, context):
    choice  = update.message.text.strip()
    mode    = context.user_data.get("therapy_mode")
    user_id = update.effective_user.id
    if mode == "cbt":
        technique = get_cbt_technique(choice)
        if not technique:
            await update.message.reply_text("Please reply with 1, 2, or 3.")
            return THERAPY_SELECT
        context.user_data.update({"current_technique": technique, "therapy_step": 0, "therapy_data": {}})
        await update.message.reply_text(technique["steps"][0]["prompt"])
        return THERAPY_STEP
    elif mode == "dbt":
        skill = get_dbt_skill(choice)
        if not skill:
            await update.message.reply_text("Please reply with 1, 2, or 3.")
            return THERAPY_SELECT
        await update.message.reply_text(skill["content"])
        _log_therapy_session(user_id, "dbt", skill["name"])
        return ConversationHandler.END
    elif mode == "mindfulness":
        exercise = get_mindfulness_exercise(choice)
        if not exercise:
            await update.message.reply_text("Please reply with 1, 2, or 3.")
            return THERAPY_SELECT
        if exercise.get("is_single_step"):
            await update.message.reply_text(exercise["content"])
            _log_therapy_session(user_id, "mindfulness", exercise["name"])
            return ConversationHandler.END
        context.user_data.update({"current_exercise": exercise, "therapy_step": 0})
        await update.message.reply_text(exercise["steps"][0])
        return THERAPY_STEP
    await update.message.reply_text("Please use /cbt, /dbt, or /mindfulness.")
    return ConversationHandler.END

async def therapy_step_handler(update, context):
    technique = (context.user_data.get("current_technique") or context.user_data.get("current_exercise"))
    if not technique:
        return ConversationHandler.END
    steps    = technique["steps"]
    step_idx = context.user_data.get("therapy_step", 0)
    key = steps[step_idx].get("key", f"step_{step_idx}")
    context.user_data.setdefault("therapy_data", {})[key] = update.message.text
    step_idx += 1
    if step_idx >= len(steps) or steps[step_idx - 1].get("final"):
        msg = (steps[step_idx - 1].get("completion_message") or technique.get("completion", "Exercise complete!"))
        await update.message.reply_text(msg)
        _log_therapy_session(update.effective_user.id, context.user_data.get("therapy_mode", "cbt"), technique["name"], completed=True)
        return ConversationHandler.END
    context.user_data["therapy_step"] = step_idx
    prompt = steps[step_idx]["prompt"].format(**context.user_data["therapy_data"])
    await update.message.reply_text(prompt)
    return THERAPY_STEP

def _log_therapy_session(user_id, module, step, completed=False):
    from modules.db.connection import get_connection, placeholder
    from datetime import datetime
    ph = placeholder()
    try:
        with get_connection() as conn:
            conn.cursor().execute(
                f"INSERT INTO therapy_sessions (user_id, module, step, completed, completed_at) VALUES ({ph},{ph},{ph},{ph},{ph})",
                (user_id, module, step, 1 if completed else 0, datetime.utcnow() if completed else None)
            )
    except Exception as e:
        logger.warning(f"Could not log therapy session: {e}")

therapy_handler = ConversationHandler(
    entry_points=[
        CommandHandler("cbt",         cbt_command),
        CommandHandler("dbt",         dbt_command),
        CommandHandler("mindfulness", mindfulness_command),
    ],
    states={
        THERAPY_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, therapy_select)],
        THERAPY_STEP:   [MessageHandler(filters.TEXT & ~filters.COMMAND, therapy_step_handler)],
    },
    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
)


# ============================================================
# v2 — Psychoeducation + Companion (Day 5)
# ============================================================

async def learn_command(update, context):
    await update.message.reply_text(PSYCHOED_MENU)
    return PSYCHOED_SELECT

async def psychoed_select(update, context):
    topic = get_topic(update.message.text.strip())
    if not topic:
        await update.message.reply_text("Please reply with 1, 2, 3, or 4.")
        return PSYCHOED_SELECT
    context.user_data["psychoed_topic"] = topic
    context.user_data["psychoed_page"]  = 0
    await update.message.reply_text(topic["content"][0])
    if len(topic["content"]) > 1:
        await update.message.reply_text("Type 'next' for more, or /menu to stop.")
        return PSYCHOED_PAGE
    return ConversationHandler.END

async def psychoed_next(update, context):
    topic = context.user_data.get("psychoed_topic")
    page  = context.user_data.get("psychoed_page", 0) + 1
    context.user_data["psychoed_page"] = page
    if update.message.text.strip().lower() != "next" or page >= len(topic["content"]):
        return ConversationHandler.END
    await update.message.reply_text(topic["content"][page])
    if page + 1 < len(topic["content"]):
        await update.message.reply_text("Type 'next' to continue.")
        return PSYCHOED_PAGE
    return ConversationHandler.END

learn_handler = ConversationHandler(
    entry_points=[CommandHandler("learn", learn_command)],
    states={
        PSYCHOED_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, psychoed_select)],
        PSYCHOED_PAGE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, psychoed_next)],
    },
    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
)

async def journal_command(update, context):
    await update.message.reply_text(f"📓 Journal Prompt\n\n{get_random_journal_prompt()}\n\nTake your time. I am listening.")

async def checkin_command(update, context):
    await update.message.reply_text(CHECK_IN_MESSAGE)

async def general_message_handler(update, context):
    """Empathetic fallback for free-form messages."""
    count = context.user_data.get("interaction_count", 0) + 1
    context.user_data["interaction_count"] = count
    if should_show_anti_parasocial(count):
        await update.message.reply_text(
            get_anti_parasocial_reminder() + "\n\nI care about your overall wellbeing. 💙"
        )
    text_lower = update.message.text.lower()
    if any(w in text_lower for w in ["sad", "depressed", "down", "low", "terrible"]):
        category = "sad"
    elif any(w in text_lower for w in ["anxious", "worried", "nervous", "stressed", "panic"]):
        category = "anxious"
    elif any(w in text_lower for w in ["happy", "great", "good", "amazing", "wonderful"]):
        category = "happy"
    else:
        category = "neutral"
    await update.message.reply_text(get_empathy_response(category))


# ============================================================
# v2 — Crisis Detection (Day 6)
# ============================================================

async def crisis_aware_message_handler(update, context):
    """Highest priority handler — checks every message for crisis signals."""
    if not update.message or not update.message.text:
        return
    text    = update.message.text
    user_id = update.effective_user.id
    assessment = assess_crisis(text)
    if assessment.severity == CrisisSeverity.NONE:
        return
    log_crisis_event(user_id, text, assessment.severity)
    try:
        from modules.db.user_profile import get_or_create_user
        profile = get_or_create_user(user_id)
        region  = profile.get("region", DEFAULT_REGION) or DEFAULT_REGION
    except Exception:
        region = DEFAULT_REGION
    if assessment.requires_resource_provision:
        response = format_crisis_response(assessment.severity, region)
        if response:
            await update.message.reply_text(response)
    if assessment.severity == CrisisSeverity.LOW:
        await update.message.reply_text(
            "It sounds like you are going through a really tough time. I am here. 💙\n\n"
            "Would you like to try a breathing exercise (/cbt) or just talk?"
        )


SUPPORTED_REGIONS = {
    "IN": "India", "US": "United States",
    "GB": "United Kingdom", "AU": "Australia", "CA": "Canada",
}

async def setregion_command(update, context):
    region_list = "\n".join(f"{code} - {name}" for code, name in SUPPORTED_REGIONS.items())
    await update.message.reply_text(
        f"🌍 Set Your Region\n\nReply with your country code:\n{region_list}\n\nOr type DEFAULT."
    )
    context.user_data["awaiting_region"] = True

async def handle_region_input(update, context):
    if not context.user_data.get("awaiting_region"):
        return
    code = update.message.text.strip().upper()
    if code in SUPPORTED_REGIONS or code == "DEFAULT":
        from modules.db.user_profile import update_user_region
        update_user_region(update.effective_user.id, code)
        context.user_data.pop("awaiting_region", None)
        await update.message.reply_text(f"✅ Region set to: {SUPPORTED_REGIONS.get(code, 'International')}")
    else:
        await update.message.reply_text(f"Please reply with: {', '.join(SUPPORTED_REGIONS.keys())} or DEFAULT")

async def deletedata_command(update, context):
    await update.message.reply_text(
        "⚠️ Delete All Data\n\nThis permanently deletes ALL your data.\n\n"
        "Type DELETE to confirm, or anything else to cancel."
    )
    context.user_data["awaiting_delete_confirm"] = True

async def handle_delete_confirm(update, context):
    if not context.user_data.get("awaiting_delete_confirm"):
        return
    context.user_data.pop("awaiting_delete_confirm", None)
    if update.message.text.strip().upper() == "DELETE":
        from modules.db.user_profile import delete_user_data
        delete_user_data(update.effective_user.id)
        await update.message.reply_text("✅ All data deleted. Start fresh with /start.")
    else:
        await update.message.reply_text("Cancelled. Your data is safe. 💙")


async def biomarker_message_hook(update, context):
    """Passive middleware on every message. Register with group=1."""
    if not update.message or not update.message.text:
        return
    if "biomarker_tracker" not in context.user_data:
        context.user_data["biomarker_tracker"] = BiomarkerTracker()
    tracker = context.user_data["biomarker_tracker"]
    tracker.record_message(update.message.text)
    if len(tracker.message_lengths) % 10 == 0:
        tracker.persist(update.effective_user.id)

async def insights_command(update, context):
    trend = get_biomarker_trend(update.effective_user.id, days=14)
    insight = build_biomarker_insight(trend)
    await update.message.reply_text(insight)
# ============================================================
# Error Handler
# ============================================================

async def error_handler(update, context):
    error = context.error
    if "Timed out" in str(error) or "ConnectError" in str(error):
        logger.warning(f"Network error (safe to ignore): {error}")
        return
    logger.error(f"Update {update} caused error: {error}", exc_info=context.error)


# ============================================================
# Entry Point
# ============================================================

if __name__ == '__main__':
    run_migrations()
    init_database()

    app = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # group=-2 → Crisis detection (HIGHEST priority)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, crisis_aware_message_handler), group=-2)

    # group=-1 → Gating handlers (disclaimer, region, delete confirm)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_disclaimer_response), group=-1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_region_input),        group=-1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_confirm),      group=-1)

    # group=0 → Commands and conversations (default)
    app.add_handler(CommandHandler("start",      start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(gad7_handler)
    app.add_handler(therapy_handler)
    app.add_handler(learn_handler)
    app.add_handler(CommandHandler("mood",       mood_command))
    app.add_handler(CommandHandler("trend",      trend_command))
    app.add_handler(CommandHandler("journal",    journal_command))
    app.add_handler(CommandHandler("checkin",    checkin_command))
    app.add_handler(CommandHandler("setregion",  setregion_command))
    app.add_handler(CommandHandler("deletedata", deletedata_command))

    # group=1 → Passive mood input
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mood_input), group=1)

    # group=2 → Empathy fallback (lowest priority)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, general_message_handler), group=2)

    app.add_error_handler(error_handler)

    print("[Bot] Starting polling...")
    app.run_polling(drop_pending_updates=True)