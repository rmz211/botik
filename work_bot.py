import logging
import asyncio
import csv
import random
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.markdown import link
from texts import TEXTS  # Импорт текстов из texts.py

# Настройки
API_TOKEN = '7766616488:AAHgpgnwaZCgZ65nekHyViNkxxPQRUH7MCs'
ADMIN_ID = 5199397925
QUOTES_FILE = "quotes.txt"
ANALYTICS_FILE = "analytics.csv"

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Основное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Основная информация"), KeyboardButton(text="Правила")],
        [KeyboardButton(text="Доступные задания"), KeyboardButton(text="Прайс-лист")],
        [KeyboardButton(text="Мои проекты"), KeyboardButton(text="Прочее")],
        [KeyboardButton(text="Сменить язык 🌐")]
    ],
    resize_keyboard=True
)

tasks_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Яндекс карты"), KeyboardButton(text="Гугл карты")],
        [KeyboardButton(text="Авито"), KeyboardButton(text="Выйти в главное меню")]
    ],
    resize_keyboard=True
)

language_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Русский 🇷🇺"), KeyboardButton(text="English 🇬🇧")]
    ],
    resize_keyboard=True
)

user_languages = {}


USERS_FILE = "users.csv"  # Файл для хранения ID пользователей

def log_user(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    # Сохраняем ID, если его еще нет в файле
    users = set()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            users = {line.strip() for line in file}
    except FileNotFoundError:
        pass

    if str(user_id) not in users:
        with open(USERS_FILE, "a", encoding="utf-8") as file:
            file.write(f"{user_id}\n")

    # Логируем в analytics.csv
    with open(ANALYTICS_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), user_id, user_name])


@dp.message(Command("start"))
async def send_welcome(message: Message):
    log_user(message)
    await bot.send_message(ADMIN_ID, f"Новый пользователь: {message.from_user.full_name} (ID: {message.from_user.id})")
    await message.answer(TEXTS["start"].format(name=message.from_user.full_name), reply_markup=main_menu)

@dp.message(lambda message: message.text == "Сменить язык 🌐")
async def change_language(message: Message):
    await message.answer(TEXTS["language_prompt"], reply_markup=language_menu)

@dp.message(lambda message: message.text in ["Русский 🇷🇺", "English 🇬🇧"])
async def set_language(message: Message):
    lang = "ru" if message.text == "Русский 🇷🇺" else "en"
    user_languages[message.from_user.id] = lang
    await message.answer(TEXTS["language_changed"][lang], reply_markup=main_menu)

@dp.message(lambda message: message.text in ["Основная информация", "Правила", "Прайс-лист", "Мои проекты", "Прочее"])
async def handle_main_menu(message: Message):
    text_map = {
        "Основная информация": TEXTS["main_info"],
        "Правила": TEXTS["rules"],
        "Прайс-лист": TEXTS["price_list"],
        "Мои проекты": TEXTS["projects"],
        "Прочее": TEXTS["other"]
    }
    await message.answer(text_map[message.text], parse_mode="Markdown")

@dp.message(lambda message: message.text == "Доступные задания")
async def handle_tasks_menu(message: Message):
    await message.answer(TEXTS["tasks_prompt"], reply_markup=tasks_menu)

@dp.message(lambda message: message.text in ["Яндекс карты", "Гугл карты", "Авито", "Выйти в главное меню"])
async def handle_tasks_submenu(message: Message):
    task_map = {
        "Яндекс карты": TEXTS["yandex_tasks"],
        "Гугл карты": TEXTS["google_tasks"],
        "Авито": TEXTS["avito_task"],
        "Выйти в главное меню": TEXTS["back_to_main"]
    }
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подать отчет", url="https://t.me/rogwork_bot")]
    ]) if message.text != "Выйти в главное меню" else main_menu

    await message.answer(task_map[message.text], parse_mode="Markdown", reply_markup=keyboard)

async def send_daily_quotes():
    while True:
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                user_ids = [line.strip() for line in file]

            with open(QUOTES_FILE, "r", encoding="utf-8") as file:
                quotes = file.readlines()

            if quotes and user_ids:
                random_quote = random.choice(quotes).strip()
                for user_id in user_ids:
                    try:
                        await bot.send_message(user_id, f"💡 _{random_quote}_", parse_mode="Markdown")
                    except Exception as e:
                        print(f"Не удалось отправить сообщение {user_id}: {e}")

        except Exception as e:
            print(f"Ошибка в send_daily_quotes: {e}")

        await asyncio.sleep(600)  # Отправка каждый час

async def main():
    logging.info("Бот запущен!")
    asyncio.create_task(send_daily_quotes())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

