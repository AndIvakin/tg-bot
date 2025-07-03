from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta

def build_calendar(year, month):
    keyboard = []
    keyboard.append([
        InlineKeyboardButton(f"{datetime(year,month,1).strftime('%B %Y')}", callback_data="IGNORE")
    ])
    buttons = [InlineKeyboardButton(d, callback_data="IGNORE") for d in "Mo Tu We Th Fr Sa Su".split()]
    keyboard.append(buttons)
    first_day = datetime(year, month, 1)
    start_day = first_day.weekday()
    days_in_month = (first_day.replace(month=month%12+1, day=1) - timedelta(days=1)).day
    row = []
    for _ in range((start_day+1)%7):
        row.append(InlineKeyboardButton(" ", callback_data="IGNORE"))
    for day in range(1, days_in_month+1):
        row.append(InlineKeyboardButton(str(day), callback_data=f"DAY_{year}-{month}-{day}"))
        if len(row) == 7:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([
        InlineKeyboardButton("<", callback_data=f"PREV_{year}_{month}"),
        InlineKeyboardButton(" ", callback_data="IGNORE"),
        InlineKeyboardButton(">", callback_data=f"NEXT_{year}_{month}")
    ])
    return InlineKeyboardMarkup(keyboard)
