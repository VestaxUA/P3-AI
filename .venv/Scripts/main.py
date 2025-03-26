import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "7701327925:AAHNql6jlwsOCEZHlq_J_Z5iP_zNAImPCT0"

# Ініціалізація бота та диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Підключення до бази даних SQLite
conn = sqlite3.connect("rental_bot.db")
cursor = conn.cursor()

# Створення таблиць
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    name TEXT,
    phone TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS rentals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    car_type TEXT,
    fuel_type TEXT,
    transmission TEXT,
    extras TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)''')
conn.commit()

# Клавіатури
main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🚗 Орендувати авто")],
    [KeyboardButton(text="📜 Умови оренди")],
    [KeyboardButton(text="📞 Залишити контакт", request_contact=True)]
], resize_keyboard=True)

car_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Авто A")],
    [KeyboardButton(text="Авто B")],
    [KeyboardButton(text="Авто C")]
], resize_keyboard=True)

fuel_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Бензин")],
    [KeyboardButton(text="Дизель")],
    [KeyboardButton(text="Електро")]
], resize_keyboard=True)

transmission_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Механіка")],
    [KeyboardButton(text="Автомат")]
], resize_keyboard=True)

extras_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="GPS навігація")],
    [KeyboardButton(text="Дитяче крісло")],
    [KeyboardButton(text="Безкоштовний драйвер")]
], resize_keyboard=True)

# Станова машина
class RentCarState(StatesGroup):
    car_type = State()
    fuel_type = State()
    transmission = State()
    extras = State()

# Обробник команди /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привіт! Я бот для оренди авто. Оберіть дію:", reply_markup=main_menu)

# Перегляд умов оренди
@dp.message(F.text == "📜 Умови оренди")
async def rental_conditions(message: Message):
    conditions_text = """📌 *Умови оренди авто:*
- Мінімальний вік водія: 21 рік
- Наявність водійського посвідчення (мінімум 2 роки стажу)
- Оренда від 1 дня
- Депозит залежить від класу авто
- Паливо: авто здається з повним баком, повертається з повним
- Штрафи за порушення ПДР покладаються на орендаря
    """
    await message.answer(conditions_text, parse_mode="Markdown", reply_markup=main_menu)

# Початок оренди авто
@dp.message(F.text == "🚗 Орендувати авто")
async def rent_car(message: Message, state: FSMContext):
    await message.answer("Оберіть тип авто:", reply_markup=car_menu)
    await state.set_state(RentCarState.car_type)

# Обробник вибору авто
@dp.message(RentCarState.car_type)
async def choose_car(message: Message, state: FSMContext):
    await state.update_data(car_type=message.text)
    await message.answer("Оберіть тип пального:", reply_markup=fuel_menu)
    await state.set_state(RentCarState.fuel_type)

# Обробник вибору пального
@dp.message(RentCarState.fuel_type)
async def choose_fuel(message: Message, state: FSMContext):
    await state.update_data(fuel_type=message.text)
    await message.answer("Оберіть тип коробки передач:", reply_markup=transmission_menu)
    await state.set_state(RentCarState.transmission)

# Обробник вибору коробки передач
@dp.message(RentCarState.transmission)
async def choose_transmission(message: Message, state: FSMContext):
    await state.update_data(transmission=message.text)
    await message.answer("Оберіть додаткові опції:", reply_markup=extras_menu)
    await state.set_state(RentCarState.extras)

# Обробник вибору додаткових опцій
@dp.message(RentCarState.extras)
async def choose_extras(message: Message, state: FSMContext):
    await state.update_data(extras=message.text)
    user_data = await state.get_data()

    # Додавання оренди в базу даних
    cursor.execute('''INSERT INTO rentals (user_id, car_type, fuel_type, transmission, extras)
                      VALUES (?, ?, ?, ?, ?)''', (message.from_user.id, user_data['car_type'], user_data['fuel_type'], user_data['transmission'], user_data['extras']))
    conn.commit()

    await message.answer(f"✅ Ваша оренда успішно оформлена!\n\n"
                         f"🚗 *Тип авто:* {user_data['car_type']}\n"
                         f"⛽ *Тип пального:* {user_data['fuel_type']}\n"
                         f"⚙ *Коробка передач:* {user_data['transmission']}\n"
                         f"🎁 *Додаткові опції:* {user_data['extras']}",
                         parse_mode="Markdown", reply_markup=main_menu)
    await state.clear()

# Обробник збереження контакту
@dp.message(F.contact)
async def save_contact(message: Message):
    contact = message.contact
    cursor.execute("REPLACE INTO users (telegram_id, name, phone) VALUES (?, ?, ?)",
                   (contact.user_id, contact.first_name, contact.phone_number))
    conn.commit()
    await message.answer("✅ Ваш контакт збережено!", reply_markup=main_menu)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
