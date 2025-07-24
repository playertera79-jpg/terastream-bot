import json
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# Setup trial tracker
TRIAL_FILE = "trials.json"
if os.path.exists(TRIAL_FILE):
    with open(TRIAL_FILE, "r") as f:
        user_trials = json.load(f)
else:
    user_trials = {}

# Load config
with open("config.json") as f:
    cfg = json.load(f)
FREE_TRIAL = cfg.get("free_trial_count", 1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 *Tera Player Bot* 🌟\n\n"
        "Send me a TeraBox link and I'll give you a direct video link (One free trial).",
        parse_mode="Markdown"
    )

def extract_direct_link(terabox_url: str) -> str:
    # Placeholder: replace with working scraper logic
    response = requests.get(f"https://teraboxdummy.api/install?url={terabox_url}")
    # Example: {"direct_link":"https://cdn.terabox.com/.../video.mp4"}
    return response.json().get("direct_link")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = str(update.effective_user.id)
    text = update.message.text.strip()
    if "terabox.com" not in text:
        return await update.message.reply_text("❌ Please send a valid TeraBox link.")

    used = user_trials.get(user, 0)
    if used >= FREE_TRIAL:
        return await update.message.reply_text(
            "🔒 Trial used! Please subscribe for ₹49/month to continue. Payment link coming soon."
        )

    # Deduct trial
    user_trials[user] = used + 1
    with open(TRIAL_FILE, "w") as f:
        json.dump(user_trials, f)

    # Extract and send
    await update.message.reply_text("⏳ Fetching your direct link...")
    direct = extract_direct_link(text)
    if direct:
        await update.message.reply_text(f"🎉 Here is your direct MP4 link:\n{direct}")
    else:
        await update.message.reply_text("⚠️ Sorry, couldn't extract the video link.")

app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    app.run_polling()
