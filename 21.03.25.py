import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "7238350264:AAHSWoKaYWF8zLm3FXLjp5VmGHA1DuFtITs"  # Замените на ваш токен
ADMIN_CHAT_ID = -1002396820471 # Замените на ID вашего админского чата

user_data = {}  # Храним временные данные пользователей





#ПРОМОКОДЫ ЗДЕСЬ, ОЛЕГ!!!!!!!!!!!
PROMO_CODES = ["MLFAST", "MLWELCOME"]






# Функция генерации случайного номера заказа
def generate_order_number():
    letters = ''.join(random.choice(string.ascii_uppercase) for i in range(4))
    numbers = ''.join(random.choice(string.digits) for i in range(4))
    return letters + numbers

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🚀 Начать заказ", callback_data="start_order")],
        [InlineKeyboardButton("📜 Как правильно оформить заказ?", callback_data="how_to_order")],
        [InlineKeyboardButton("🧮 Калькулятор стоимости", callback_data="cost_calculator")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("👋 Привет! Чтобы сделать заказ, нажмите кнопку ниже.", reply_markup=reply_markup)

# Обработчик кнопок

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()  # Закрываем "часики" на кнопке

    if query.data == "start_order":
        user_data[user_id] = {}  # Очищаем предыдущие данные
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("✏ Введите артикул:", reply_markup=reply_markup)

    elif query.data == "back_to_start":
        keyboard = [
            [InlineKeyboardButton("🚀 Начать заказ", callback_data="start_order")],
            [InlineKeyboardButton("📜 Как правильно оформить заказ?", callback_data="how_to_order")],
            [InlineKeyboardButton("🧮 Калькулятор стоимости", callback_data="cost_calculator")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("👋 Привет! Чтобы сделать заказ, нажмите кнопку ниже.", reply_markup=reply_markup)

    elif query.data == "how_to_order":
        keyboard = [[InlineKeyboardButton("✅ Прочитал", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        how_to_order_text = """📌 Инструкция:https://telegra.ph/Kak-oformit-zakaz-cherez-POIZON-03-09"""
        await query.message.edit_text(how_to_order_text, reply_markup=reply_markup, disable_web_page_preview=True)

    elif query.data == "cost_calculator":
        user_data[user_id] = {"awaiting_cost_input": True}  # Устанавливаем флаг ожидания стоимости
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("💰 Введите стоимость товара (в юанях):", reply_markup=reply_markup)

    elif query.data == "skip_screenshot":
        user_data[user_id]["screenshot"] = None
        await send_delivery_options(query)

    elif query.data.startswith("delivery_"):
        delivery_method = query.data.split("_")[1]
        delivery_text = {
            "auto": "🚛 Авто (20-30 дней)",
            "air": "✈ Авиа (12-20 дней)",
            "express": "⚡ Экспресс (6-8 дней)",
        }.get(delivery_method, "❓ Неизвестно")

        user_data[user_id]["delivery"] = delivery_text
        user_data[user_id]["awaiting_promo"] = True  # Устанавливаем флаг ожидания промокода

        keyboard = [[InlineKeyboardButton("⏭ Пропустить", callback_data="skip_promo")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text("🎁 Введите промокод (если есть):", reply_markup=reply_markup)

    elif query.data == "skip_promo":
        await finalize_order(query, context)
    
    elif query.data == "retry_promo":
        keyboard = [[InlineKeyboardButton("⏭ Пропустить", callback_data="skip_promo")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text("🎁 Введите промокод (если есть):", reply_markup=reply_markup)

# Обработчик текстовых сообщений

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_input = update.message.text

    # Обработка ввода стоимости товара
    if user_id in user_data and user_data[user_id].get("awaiting_cost_input"):  
        if user_input.isdigit() and int(user_input) > 0:
            x = int(user_input)
            calculated_cost = ((x * 13 * 1.06) + 1500)
            final_cost = round(calculated_cost / 100) * 100  # Округление до сотен в большую сторону

            keyboard = [
                [InlineKeyboardButton("🔄 Рассчитать стоимость еще раз", callback_data="cost_calculator")],
                [InlineKeyboardButton("🏠 Вернуться на главную", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(f"💰 Стоимость товара без учета доставки составляет: {final_cost}₽", reply_markup=reply_markup)

        else:
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("❌ Ошибка, повторите попытку:", reply_markup=reply_markup)

        user_data.pop(user_id)  # Удаляем флаг, чтобы бот не путал ввод с последующими командами

    # Обработка ввода артикула
    elif user_id in user_data and "artikel" not in user_data[user_id]:
        user_data[user_id]["artikel"] = user_input
        keyboard = [[InlineKeyboardButton("Назад", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Введите размер:", reply_markup=reply_markup)

    # Обработка ввода размера
    elif user_id in user_data and "size" not in user_data[user_id]:
        user_data[user_id]["size"] = user_input
        keyboard = [[InlineKeyboardButton("Пропустить", callback_data="skip_screenshot")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Если есть несколько вариантов товара, отправьте скриншот с желаемым вариантом:", reply_markup=reply_markup)

    # Обработка ввода промокода
    elif user_id in user_data and user_data[user_id].get("awaiting_promo"):
        user_data[user_id]["awaiting_promo"] = False  # Сбрасываем флаг ожидания

        if user_input in PROMO_CODES:
            user_data[user_id]["promo"] = user_input
            await update.message.reply_text("Промокод успешно применен!")

            await finalize_order(update, context, user_id)

        else:
            keyboard = [
                [InlineKeyboardButton("Ввести еще раз", callback_data="retry_promo")],
                [InlineKeyboardButton("Пропустить", callback_data="skip_promo")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            user_data[user_id]["awaiting_promo"] = True  # Сбрасываем флаг ожидания

            await update.message.reply_text("Промокод недействителен", reply_markup=reply_markup)
# Обработчик изображений (скриншотов)
async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in user_data:
        photo = update.message.photo[-1].file_id
        user_data[user_id]["screenshot"] = photo

        await send_delivery_options(update)

# Функция выбора доставки
async def send_delivery_options(update):
    keyboard = [
        [InlineKeyboardButton("🚛 Авто (20-30 дней)", callback_data="delivery_auto")],
        [InlineKeyboardButton("✈ Авиа (12-20 дней)", callback_data="delivery_air")],
        [InlineKeyboardButton("⚡ Экспресс (6-8 дней)", callback_data="delivery_express")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if isinstance(update, Update):
        await update.message.reply_text("📦 Выберите способ доставки:", reply_markup=reply_markup)
    else:
        await update.message.edit_text("📦 Выберите способ доставки:", reply_markup=reply_markup)

#Функция промокода

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    user = update.message.from_user if update.message else update.callback_query.from_user  # Универсальный способ получить пользователя
    order_number = generate_order_number()

    final_message = (
        f"📢 Новый заказ от @{user.username or 'Пользователь без никнейма'}!\n\n"
        f"📌 Номер заказа: {order_number}\n"
        f"🛒 Артикул: {user_data[user_id].get('artikel', 'Не указан')}\n"
        f"📏 Размер: {user_data[user_id].get('size', 'Не указан')}\n"
        f"🚚 Доставка: {user_data[user_id].get('delivery', 'Не выбрано')}\n"
        f"🎁 Промокод: {user_data[user_id].get('promo', 'Не использован')}"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=final_message, parse_mode="Markdown")

    # Отправка фото (если есть)
    if user_data[user_id].get("screenshot"):
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=user_data[user_id]["screenshot"])

    warning_message = (
        f"✅Ваш заказ отправлен! 📌 Ваш номер заказа: {order_number}\n"
        f"👨‍💻 В течение суток администратор свяжется с вами.\n\n"
        f"!Внимание!\n"
        f"⚠ Если у вас в профиле отсутствует никнейм, вы должны самостоятельно написать администратору о своем заказе и уточнить все детали: @mandl_helper\n"
        f"В противном случае заказ будет отменен в течение суток."
    )

    # Отправляем сообщение пользователю
    if update.message:
        await update.message.reply_text(warning_message)
    elif update.callback_query:
        await update.callback_query.message.edit_text(warning_message)
    
# Запуск бота
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, image_handler))

    print("🤖 Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
