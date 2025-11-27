from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os
import asyncio

# --- Настройки ---
BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен из переменной окружения
if not BOT_TOKEN:
    raise ValueError("Не задан токен бота! Проверь переменную окружения BOT_TOKEN.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Хранилище данных ---
users = {}  # {user_id: [history]}
total_income = 0

# --- Команды бота ---

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! 👋\n"
        "Команды:\n"
        "/add <сумма> — добавить доход\n"
        "/remove <сумма> — снять часть дохода\n"
        "/total — общий доход всех участников\n"
        "/my — твоя история\n"
        "/top — топ участников\n"
        "/reset_user — обнулить свои данные"
    )

@dp.message(Command("add"))
async def add_income(message: types.Message):
    try:
        amount = float(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("Укажи сумму после команды, например: /add 100")
        return

    global total_income
    total_income += amount
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = []
    users[user_id].append(f"+{amount}")
    
    await message.answer(f"Добавлено {amount}. Твой доход обновлён!")

@dp.message(Command("remove"))
async def remove_income(message: types.Message):
    try:
        amount = float(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer("Укажи сумму после команды, например: /remove 50")
        return

    global total_income
    total_income -= amount
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = []
    users[user_id].append(f"-{amount}")
    
    await message.answer(f"Списано {amount}. Твой доход обновлён!")

@dp.message(Command("total"))
async def show_total(message: types.Message):
    await message.answer(f"Общий доход всех участников: {total_income}")

@dp.message(Command("my"))
async def show_my_history(message: types.Message):
    user_id = message.from_user.id
    history = users.get(user_id, [])
    if not history:
        await message.answer("У тебя пока нет записей.")
    else:
        await message.answer("Твоя история:\n" + "\n".join(history))

@dp.message(Command("top"))
async def show_top(message: types.Message):
    if not users:
        await message.answer("Пока нет участников.")
        return
    result = []
    for user_id, records in users.items():
        total = sum(float(r) for r in records)
        result.append((total, user_id))
    result.sort(reverse=True)
    text = "Топ участников:\n"
    for total, user_id in result[:10]:
        text += f"{user_id}: {total}\n"
    await message.answer(text)

@dp.message(Command("reset_user"))
async def reset_user(message: types.Message):
    user_id = message.from_user.id
    if user_id in users:
        del users[user_id]
    await message.answer("Твои данные обнулены.")

# --- Запуск бота ---
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
