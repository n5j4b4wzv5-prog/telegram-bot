import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
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

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("👋 Привет! Напиши /setup в группе.")

@dp.message(Command("setup"))
async def setup_cmd(message: types.Message):
    global group_id
    if message.chat.type != "supergroup":
        return await message.reply("❌ Это не супергруппа!")
    data["group_id"] = message.chat.id
    group_id = message.chat.id
    save_data(data)
    await message.reply(f"✅ Группа сохранена!")

@dp.message(Command("status"))
async def status_cmd(message: types.Message):
    if not group_id:
        await message.answer("ℹ️ Бот не настроен.")
    else:
        await message.answer(f"📊 Группа: {group_id}\n📌 Топиков: {len(user_topics)}")

@dp.message(lambda msg: msg.chat.type == "private" and not msg.text.startswith("/"))
async def handle_msg(message: types.Message):
    if not group_id:
        return await message.answer("🔧 Бот не настроен.")
    
    uid = str(message.from_user.id)
    tid = user_topics.get(uid)
    
    if not tid:
        try:
            topic = await bot.create_forum_topic(
                chat_id=group_id,
                name=f"💬 {message.from_user.full_name}"
            )
            tid = topic.message_thread_id
            user_topics[uid] = tid
            data["user_topics"] = user_topics
            save_data(data)
        except Exception as e:
            return await message.answer(f"❌ Ошибка: {e}")
    
    try:
        await bot.send_message(
            chat_id=group_id,
            message_thread_id=tid,
            text=f"💬 {message.from_user.full_name}:\n{message.text}"
        )
        await message.answer("✅ Отправлено!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

async def main():
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
