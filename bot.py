import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

# Load .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Conversation States
ASK_COUNT = 1

# Store email temporarily
user_email = {}

# Function to generate variations
def generate_case_variations(email):
    username, domain = email.split('@')
    variations = set()
    total = 2 ** len(username)

    for i in range(total):
        variation = ''
        for j in range(len(username)):
            if (i >> j) & 1:
                variation += username[j].upper()
            else:
                variation += username[j].lower()
        variations.add(f"{variation}@{domain}")
    return sorted(list(variations))

# /start command
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the Email Variation Generator Bot!\n\n"
        "👉 Use:\n/email your_email@example.com"
    )

# /email command starts conversation
async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /email your_email@example.com")
        return ConversationHandler.END

    email = context.args[0]
    if '@' not in email:
        await update.message.reply_text("❌ Invalid email format.")
        return ConversationHandler.END

    user_email[update.effective_user.id] = email
    await update.message.reply_text("✏️ How many email variations do you want?")
    return ASK_COUNT

# User responds with count
async def ask_count_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = int(update.message.text.strip())
        email = user_email.get(update.effective_user.id)

        all_variations = generate_case_variations(email)
        limited_variations = all_variations[:count]

        numbered = [f"{i+1}: {v}" for i, v in enumerate(limited_variations)]

        # Split into chunks for Telegram limits
        reply_chunks = []
        chunk = ""
        for line in numbered:
            if len(chunk) + len(line) + 1 < 4000:
                chunk += line + "\n"
            else:
                reply_chunks.append(chunk)
                chunk = line + "\n"
        if chunk:
            reply_chunks.append(chunk)

        await update.message.reply_text(f"✅ Sending {len(limited_variations)} variations:")
        for part in reply_chunks:
            await update.message.reply_text(part)

    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number.")
    return ConversationHandler.END

# Cancel fallback
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END

# Main
if __name__ == "__main__":
    if not TOKEN:
        print("❌ BOT_TOKEN missing.")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()

    # Conversation handler for /email
    email_conversation = ConversationHandler(
        entry_points=[CommandHandler("email", email_handler)],
        states={
            ASK_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_count_handler)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(email_conversation)

    print("🤖 Bot is running...")
    app.run_polling()
