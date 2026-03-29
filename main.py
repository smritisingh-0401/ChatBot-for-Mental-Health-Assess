# ADD to imports at top of main.py:
from modules.safety.disclaimer import (
    DISCLAIMER_TEXT, has_accepted_disclaimer, record_disclaimer_acceptance
)
from modules.db.schema import run_migrations

# ADD: call run_migrations() inside your main() function, before run_polling()

# ── Replace your existing start_command handler ───────────────────────────
async def start_command(update, context):
    user = update.effective_user
    if not has_accepted_disclaimer(user.id):
        await update.message.reply_text(DISCLAIMER_TEXT, parse_mode="MarkdownV2")
        context.user_data["awaiting_disclaimer"] = True
        return
    await update.message.reply_text(
        f"Welcome back, {user.first_name}! Use /menu to see all options."
    )

async def handle_disclaimer_response(update, context):
    """Intercepts any message while disclaimer is pending."""
    if not context.user_data.get("awaiting_disclaimer"):
        return
    if update.message.text.strip().upper() == "AGREE":
        user = update.effective_user
        record_disclaimer_acceptance(user.id, user.username)
        context.user_data.pop("awaiting_disclaimer", None)
        await update.message.reply_text(
            "✅ Thank you! You're all set.\n\nType /menu to see what I can help with."
        )
    else:
        await update.message.reply_text(
            "Please type AGREE to continue, or /start to restart."
        )

# Register BEFORE other handlers (group=-1):
# application.add_handler(
#     MessageHandler(filters.TEXT & ~filters.COMMAND, handle_disclaimer_response),
#     group=-1
# )