import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DATA_FILE = "topics.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"group_id": None, "user_topics": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()
group_id = data.get("group_id")
user_topics = data.get("user_topics", {})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я бот.")

async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global group_id
    if update.message.chat.type != "supergroup":
        await update.message.reply_text("❌ Это не супергруппа!")
        return
    data["group_id"] = update.message.chat.id
    group_id = update.message.chat.id
    save_data(data)
    await update.message.reply_text("✅ Группа сохранена!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not group_id:
        await update.message.reply_text("ℹ️ Бот не настроен.")
    else:
        await update.message.reply_text(f"📊 Группа: {group_id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not group_id:
        await update.message.reply_text("🔧 Бот не настроен.")
        return
    
    user = update.message.from_user
    uid = str(user.id)
    tid = user_topics.get(uid)
    
    if not tid:
        try:
            topic = await context.bot.create_forum_topic(
                chat_id=group_id,
                name=f"{user.full_name}"
            )
            tid = topic.message_thread_id
            user_topics[uid] = tid
            data["user_topics"] = user_topics
            save_data(data)
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
            return
    
    try:
        await context.bot.send_message(
            chat_id=group_id,
            message_thread_id=tid,
            text=f"{user.full_name}:\n{update.message.text}"
        )
        await update.message.reply_text("✅ Отправлено!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setup", setup))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
