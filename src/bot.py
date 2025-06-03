import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load token from .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

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
        "👉 Use the command below to generate variations:\n"
        "/email your_email@example.com"
    )

# /email command
async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /email your_email@example.com")
        return

    email = context.args[0]

    if '@' not in email:
        await update.message.reply_text("❌ Invalid email format.")
        return

    variations = generate_case_variations(email)

    # Add serial number before each email
    numbered_variations = [f"{i+1}: {email}" for i, email in enumerate(variations)]

    # Combine into a single message or send in parts
    reply_chunks = []
    chunk = ""
    for line in numbered_variations:
        if len(chunk) + len(line) + 1 < 4000:
            chunk += line + "\n"
        else:
            reply_chunks.append(chunk)
            chunk = line + "\n"
    if chunk:
        reply_chunks.append(chunk)

    await update.message.reply_text(f"✅ {len(variations)} variations generated. Sending:")
    for part in reply_chunks:
        await update.message.reply_text(part)

# Run bot
if __name__ == "__main__":
    if not TOKEN:
        print("❌ BOT_TOKEN not found in .env")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("email", email_handler))

    print("🤖 Bot is running...")
    app.run_polling()