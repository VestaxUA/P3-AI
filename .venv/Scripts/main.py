import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database import init_db, add_user, add_rental

TOKEN = "7017982855:AAFDOv-JxBtI59tA5qeCRzios-a6c93gdxE"
bot = telebot.TeleBot(TOKEN)

init_db()

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Поділитися контактом", request_contact=True))
    markup.add(KeyboardButton("Умови оренди"))
    markup.add(KeyboardButton("Орендувати авто"))
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Ласкаво просимо до сервісу оренди авто!", reply_markup=main_menu())

@bot.message_handler(content_types=["contact"])
def handle_contact(message):
    if message.contact is not None:
        user_id = message.contact.user_id
        name = message.contact.first_name
        phone = message.contact.phone_number
        add_user(user_id, name, phone)
        bot.send_message(message.chat.id, "Контакт збережено! Що хочете зробити далі?", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "Умови оренди")
def rental_terms(message):
    text = "🔹 Мінімальний термін оренди: 1 день\n🔹 Депозит: від 500 грн\n🔹 Водійський стаж: від 2 років"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == "Орендувати авто")
def choose_car_type(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Седан", "Позашляховик")
    markup.add("Мінівен", "Спорткар")
    bot.send_message(message.chat.id, "Оберіть тип авто:", reply_markup=markup)
    bot.register_next_step_handler(message, choose_fuel_type)

def choose_fuel_type(message):
    car_type = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Бензин", "Дизель")
    markup.add("Електро", "Гібрид")
    bot.send_message(message.chat.id, "Оберіть тип пального:", reply_markup=markup)
    bot.register_next_step_handler(message, choose_transmission, car_type)

def choose_transmission(message, car_type):
    fuel_type = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Механіка", "Автомат")
    bot.send_message(message.chat.id, "Оберіть тип коробки передач:", reply_markup=markup)
    bot.register_next_step_handler(message, choose_extras, car_type, fuel_type)

def choose_extras(message, car_type, fuel_type):
    transmission = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Дитяче крісло", "Навігатор", "Без доповнень")
    bot.send_message(message.chat.id, "Оберіть додаткові опції:", reply_markup=markup)
    bot.register_next_step_handler(message, confirm_rental, car_type, fuel_type, transmission)

def confirm_rental(message, car_type, fuel_type, transmission):
    extras = message.text
    user_id = message.chat.id

    add_rental(user_id, car_type, fuel_type, transmission, extras)

    bot.send_message(message.chat.id, f"✅ Ви успішно орендували авто:\n"
                                      f"🚗 Тип: {car_type}\n"
                                      f"⛽ Пальне: {fuel_type}\n"
                                      f"⚙ Коробка передач: {transmission}\n"
                                      f"🔹 Додатково: {extras}",
                     reply_markup=main_menu())

bot.polling()
