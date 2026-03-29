import nest_asyncio
nest_asyncio.apply()

import sys
import asyncio
import threading
import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import init_database, save_user, save_conversation, save_assessment, get_user_assessments
from depression_detector import DepressionDetector, PHQ9_QUESTIONS

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

init_database()
detector = DepressionDetector()

(
    START, MENU, ASSESSMENT_START, ASKING_QUESTION,
    ASSESSMENT_RESULT, SUPPORT, END
) = range(7)

user_assessments = {}


# ============================================
# Handler Functions
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('Handler triggered!')
    """Handle /start command"""
    logger.info(f"Start command from user: {update.effective_user.id}")
    user = update.effective_user
    save_user(user.id, user.username, user.first_name, user.last_name)
    
    welcome_message = f"""
👋 Welcome to MindCare Bot, {user.first_name}!

I'm here to help you understand your mental health through a scientifically-backed assessment.

This chatbot can:
✅ Conduct a depression screening (PHQ-9)
✅ Provide personalized insights
✅ Suggest helpful resources
✅ Maintain confidential records

⚠️ Important: This bot is NOT a substitute for professional medical advice.
Always consult a mental health professional for diagnosis and treatment.

What would you like to do?
"""
    keyboard = [
        [InlineKeyboardButton("📋 Start Assessment", callback_data='start_assessment')],
        [InlineKeyboardButton("📊 View Previous Results", callback_data='view_results')],
        [InlineKeyboardButton("❓ Help & Resources", callback_data='resources')],
        [InlineKeyboardButton("🚪 Exit", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    return MENU


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display main menu"""
    logger.info(f"Show menu for user: {update.effective_user.id}")
    query = update.callback_query
    await query.answer()
    
    menu_message = """
📋 MindCare Main Menu

What would you like to do today?
"""
    keyboard = [
        [InlineKeyboardButton("📋 Start Assessment", callback_data='start_assessment')],
        [InlineKeyboardButton("📊 View Previous Results", callback_data='view_results')],
        [InlineKeyboardButton("❓ Help & Resources", callback_data='resources')],
        [InlineKeyboardButton("🚪 Exit", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(menu_message, reply_markup=reply_markup)
    return MENU


async def start_assessment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start PHQ-9 assessment"""
    logger.info(f"Start assessment for user: {update.effective_user.id}")
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    user_assessments[user_id] = {'current_question': 0, 'answers': [], 'user_id': user_id}
    
    instruction = """
🧠 Depression Screening Assessment (PHQ-9)

You'll answer 9 questions about how you've been feeling over the past 2 weeks.

For each question, choose:
• 😊 Not at all (0)
• 😔 Several days (1)
• 😞 More than half the days (2)
• 😢 Nearly every day (3)

Your responses are confidential and saved securely.

Let's begin! 👇
"""
    await query.edit_message_text(instruction)
    await asyncio.sleep(0.5)
    await ask_phq9_question(update, context)
    return ASKING_QUESTION


async def ask_phq9_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask the next PHQ-9 question"""
    user_id = update.effective_user.id
    
    if user_id not in user_assessments:
        user_assessments[user_id] = {'current_question': 0, 'answers': []}
    
    assessment = user_assessments[user_id]
    question_idx = assessment['current_question']
    
    if question_idx >= len(PHQ9_QUESTIONS):
        await show_assessment_result(update, context)
        return ASSESSMENT_RESULT
    
    question = PHQ9_QUESTIONS[question_idx]
    
    keyboard = [
        [InlineKeyboardButton("😊 Not at all", callback_data='answer_0')],
        [InlineKeyboardButton("😔 Several days", callback_data='answer_1')],
        [InlineKeyboardButton("😞 More than half", callback_data='answer_2')],
        [InlineKeyboardButton("😢 Nearly every day", callback_data='answer_3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    progress = f"Question {question_idx + 1}/9"
    message_text = f"{progress}\n\n{question}"
    
    query = update.callback_query
    if query:
        try:
            await query.edit_message_text(message_text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            await query.message.reply_text(message_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message_text, reply_markup=reply_markup)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle answer to PHQ-9 question"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if user_id not in user_assessments:
        await query.edit_message_text("Session expired. Please start again with /start")
        return MENU
    
    try:
        answer_value = int(data.split('_')[1])
    except (IndexError, ValueError):
        logger.error(f"Invalid answer data: {data}")
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
    """Calculate and display assessment results"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    logger.info(f"Show assessment result for user: {user_id}")
    
    if user_id not in user_assessments:
        await query.edit_message_text("Session expired.")
        return MENU
    
    assessment = user_assessments[user_id]
    answers = assessment['answers']
    
    phq9_score = sum(answers)
    result = detector.classify_score(phq9_score)
    severity = result['severity']
    
    save_assessment(user_id, phq9_score, severity, answers)
    therapeutic_response = detector.get_therapeutic_response(result)
    
    result_message = f"""
📊 Assessment Results

{result['color']} Depression Severity: {severity}
📈 PHQ-9 Score: {phq9_score}/27

💭 Analysis:
{therapeutic_response}

📌 Next Steps:
1. Save these results for your records
2. If severe, contact a professional immediately
3. Practice self-care daily
4. Retake assessment in 2 weeks
"""
    keyboard = [
        [InlineKeyboardButton("💪 Self-Care Tips", callback_data='self_care')],
        [InlineKeyboardButton("📚 Resources", callback_data='resources')],
        [InlineKeyboardButton("↩️ Main Menu", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(result_message, reply_markup=reply_markup)
    save_conversation(user_id, "Assessment completed", result_message)


async def show_resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show mental health resources"""
    logger.info(f"Show resources for user: {update.effective_user.id}")
    query = update.callback_query
    await query.answer()
    
    resources_message = """
📚 Mental Health Resources

🌍 Global Resources:
• SAMHSA National Helpline: 1-800-662-4357
• International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/

🇺🇸 US-Specific:
• 988 Suicide & Crisis Lifeline: Call or text 988
• Crisis Text Line: Text HOME to 741741
• NAMI Helpline: 1-800-950-6264

💻 Online Resources:
• Mind.org.uk - Mental health information
• ADAA.org - Anxiety & Depression Association
• BetterHelp.com - Online therapy
• Headspace - Meditation app

⚠️ Emergency: If in immediate danger, call 911 or go to nearest ER

Remember: Seeking help is a sign of strength, not weakness. 💪
"""
    keyboard = [
        [InlineKeyboardButton("↩️ Main Menu", callback_data='menu')],
        [InlineKeyboardButton("🚪 Exit", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(resources_message, reply_markup=reply_markup)


async def show_self_care(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show self-care tips"""
    logger.info(f"Show self-care for user: {update.effective_user.id}")
    query = update.callback_query
    await query.answer()
    
    self_care_message = """
💪 Self-Care Tips for Mental Health

🛏️ Sleep:
• Maintain regular sleep schedule (7-9 hours)
• Avoid screens 1 hour before bed
• Keep bedroom cool and dark

🏃 Exercise:
• 30 minutes daily activity
• Walking, yoga, dancing all help
• Releases mood-boosting endorphins

🍎 Nutrition:
• Eat regular, balanced meals
• Stay hydrated
• Limit caffeine and alcohol

👥 Social Connection:
• Reach out to friends/family
• Join support groups
• Volunteer in community

🧘 Mindfulness:
• Meditation: 5-10 minutes daily
• Deep breathing exercises
• Journaling thoughts and feelings

🎯 Structure:
• Set daily goals
• Maintain routine
• Break tasks into small steps

Remember: Self-care isn't selfish. You deserve this support! ❤️
"""
    keyboard = [
        [InlineKeyboardButton("↩️ Main Menu", callback_data='menu')],
        [InlineKeyboardButton("🚪 Exit", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(self_care_message, reply_markup=reply_markup)


async def view_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View previous assessment results"""
    logger.info(f"View results for user: {update.effective_user.id}")
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    assessments = get_user_assessments(user_id)
    
    if not assessments:
        message = "📊 No previous assessments found.\n\nStart your first assessment to get results!"
    else:
        message = "📊 Your Assessment History:\n\n"
        for i, (score, severity, date) in enumerate(assessments[:5], 1):
            message += f"{i}. {date}\n   Score: {score}/27 - {severity}\n\n"
    
    keyboard = [
        [InlineKeyboardButton("↩️ Main Menu", callback_data='menu')],
        [InlineKeyboardButton("🚪 Exit", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks"""
    query = update.callback_query
    
    try:
        if query.data == 'menu':
            await show_menu(update, context)
            return MENU
        elif query.data == 'start_assessment':
            await start_assessment(update, context)
            return ASKING_QUESTION
        elif query.data == 'resources':
            await show_resources(update, context)
        elif query.data == 'self_care':
            await show_self_care(update, context)
        elif query.data == 'view_results':
            await view_results(update, context)
        elif query.data.startswith('answer_'):
            await handle_answer(update, context)
            return ASKING_QUESTION
        elif query.data == 'exit':
            await query.edit_message_text("👋 Thank you for using MindCare Bot. Take care of yourself!")
            return END
    except Exception as e:
        logger.error(f"Error in button callback: {e}")
        await query.answer("An error occurred. Please try again.")



# ============================================
# Entry Point with Event Loop Handling
# ============================================

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()