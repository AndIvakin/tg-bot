import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv

import storage, calendar_keyboard

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "supersecret")

BOOK_DATE = {}

async def start(u, c):
    kb = [
        [InlineKeyboardButton("Записаться", callback_data="cmd_book")],
        [InlineKeyboardButton("Моя запись", callback_data="cmd_mine")],
        [InlineKeyboardButton("📞 Админ", callback_data="cmd_admin")]
    ]
    await u.message.reply_text("Привет! Что желаете?", reply_markup=InlineKeyboardMarkup(kb))

async def callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data
    uid = update.callback_query.from_user.id
    await update.callback_query.answer()

    if data == "cmd_book":
        now = datetime.now()
        await update.callback_query.edit_message_text(
            "Выберите дату:", reply_markup=calendar_keyboard.build_calendar(now.year, now.month))
    elif data.startswith("DAY_"):
        y,m,d = map(int, data[4:].split('-'))
        date = datetime(y,m,d)
        BOOK_DATE[uid] = date
        kb = [
            [InlineKeyboardButton("10:00", callback_data="SLOT_10"), InlineKeyboardButton("11:00", callback_data="SLOT_11")],
            [InlineKeyboardButton("12:00", callback_data="SLOT_12")]
        ]
        await update.callback_query.edit_message_text(f"Выбрано {date.date()}. Выберите время:", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("SLOT_"):
        time = data.split("_")[1]
        date = BOOK_DATE.get(uid)
        slot_key = f"{date.date()} {time}:00"
        slots = storage.get_slots()
        if slot_key in slots and slots[slot_key]:
            await update.callback_query.edit_message_text("Этот слот уже занят.")
        else:
            slots[slot_key] = uid
            storage.save_slots(slots)
            await update.callback_query.edit_message_text(f"✅ Записано на {slot_key}")
    elif data == "cmd_mine":
        slots = storage.get_slots()
        mine = [s for s,u_ in slots.items() if u_==uid]
        if not mine:
            await update.callback_query.edit_message_text("У вас нет записи.")
        else:
            kb = [[InlineKeyboardButton("Отменить", callback_data=f"CAN_{mine[0]}")]]
            await update.callback_query.edit_message_text(f"Ваша запись: {mine[0]}", reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("CAN_"):
        slot = data[4:]
        slots = storage.get_slots()
        date = datetime.strptime(slot.split()[0], "%Y-%m-%d")
        if date - datetime.now() < timedelta(days=1) and not storage.is_admin(uid):
            await update.callback_query.edit_message_text("❌ Отмена разрешена только за сутки.")
        else:
            slots.pop(slot, None)
            storage.save_slots(slots)
            await update.callback_query.edit_message_text("Запись отменена.")
    elif data == "cmd_admin":
        if storage.is_admin(uid):
            await update.callback_query.edit_message_text("Вы уже админ.")
        else:
            BOOK_DATE[uid] = "ADMIN_LOGIN"
            await update.callback_query.edit_message_text("Введите пароль администратора:")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if BOOK_DATE.get(uid) == "ADMIN_LOGIN":
        if update.message.text == ADMIN_PASSWORD:
            storage.add_admin(uid)
            await update.message.reply_text("✅ Вы теперь администратор.")
        else:
            await update.message.reply_text("❌ Неверный пароль.")
        BOOK_DATE.pop(uid, None)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
