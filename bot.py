from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import Forbidden

# Кнопки главного меню (обычные)
menu_keyboard = [
    ["История", "Домоводство"],
    ["IT для \"чайников\"", "FAQ"],
    ["О боте"]
]
menu_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Получена команда /start от пользователя {update.effective_user.id}")
    try:
        await update.message.reply_text(
            "Привет! Я помощник сайта [vibegnews.tilda.ws](https://vibegnews.tilda.ws/). Выберите раздел меню:",
            reply_markup=menu_markup,
            parse_mode="Markdown"
        )
    except Forbidden:
        user_id = update.effective_user.id if update.effective_user else "неизвестный"
        print(f"Пользователь {user_id} заблокировал бота, сообщение не отправлено.")

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    try:
        if text == "История":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Подробнее на сайте", url="https://vibegnews.tilda.ws/")]
            ])
            await update.message.reply_text(
                "Лазурное — уютный поселок на берегу Черного моря в Херсонской области. "
                "Основан в 1803 году, известен своими пляжами и гостеприимством.",
                reply_markup=keyboard
            )
            await update.message.reply_text(
                "В разделе *История* вы можете узнать интересные исторические факты Причерноморья, "
                "прочитать или прослушать книги о Лазурном.",
                parse_mode="Markdown"
            )

        elif text == "Домоводство":
            await update.message.reply_text(
                "В разделе *Домоводство* представлены практические советы по уюту и эффективности в доме, "
                "рекомендации по экономии бюджета и виноградарству.",
                parse_mode="Markdown"
            )
            await update.message.reply_text(
                "*Например:*\n"
                "- Календарь садовода\n"
                "- Как быстро обменять деньги\n"
                "- Как выбрать стабилизатор напряжения\n"
                "- Можно ли бороться с растрескиванием ягод винограда",
                parse_mode="Markdown"
            )

        elif text == "IT для \"чайников\"":
            await update.message.reply_text(
                "*IT для «чайников»:* Простые и понятные советы по работе с компьютером, смартфоном и интернетом.",
                parse_mode="Markdown"
            )
            await update.message.reply_text(
                "*Например:*\n"
                "- Смартфон для пожилых\n"
                "- Статьи по искусственному интеллекту и нейросетям\n"
                "- Освоение компьютера",
                parse_mode="Markdown"
            )

        elif text == "FAQ":
            await update.message.reply_text(
                "В чате вы можете получить ответы на часто задаваемые вопросы и воспользоваться помощью бота.",
                parse_mode="Markdown"
            )

        elif text == "О боте":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Перейти на сайт", url="https://vibegnews.tilda.ws/")]
            ])
            await update.message.reply_text(
                "Бот является помощником сайта [vibegnews.tilda.ws](https://vibegnews.tilda.ws/) "
                "и даёт ответы по его темам и другим вопросам в своей компетенции.\n\n"
                "*Основные возможности:*\n"
                "- Лимит токенов: 20 токенов на пользователя в сутки.\n"
                "- Сброс лимита: раз в день.\n"
                "- Ведение статистики использования.",
                parse_mode="Markdown",
                reply_markup=keyboard
            )

        else:
            await update.message.reply_text(
                "Пожалуйста, выберите раздел из меню.",
                reply_markup=menu_markup
            )

    except Forbidden:
        user_id = update.effective_user.id if update.effective_user else "неизвестный"
        print(f"Пользователь {user_id} заблокировал бота, сообщение не отправлено.")

# Главная функция для запуска бота
def main():
    # Замените на ваш реальный токен Telegram-бота
    app = ApplicationBuilder().token("7944320544:AAESvvcWqGi7kaPlRbON3WwAq_WMsjEcH3Y").build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Бот запущен. Ожидание сообщений...")
    app.run_polling()

if __name__ == "__main__":
    main()
