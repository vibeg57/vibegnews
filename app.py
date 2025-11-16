from fastapi import FastAPI, Request
from fastapi.responses import Response
import requests

app = FastAPI()

TELEGRAM_TOKEN = "7944320544:AAESvvcWqGi7kaPlRbON3WwAq_WMsjEcH3Y"
BOT_NAME = "vibegbot"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

MAIN_MENU = [
    ["История", "Домоводство"],
    ["IT для «чайников»", "FAQ"],
    ["О боте"]
]

def send_message(chat_id, text, buttons=None, remove_keyboard=False):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    if buttons:
        payload["reply_markup"] = {"keyboard": buttons, "resize_keyboard": True}
    elif remove_keyboard:
        payload["reply_markup"] = {"remove_keyboard": True}
    requests.post(f"{BASE_URL}/sendMessage", json=payload)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    # Для отладки: print приходящих апдейтов из Telegram
    print("UPDATE FROM TG:", data)

    if "message" not in data:
        # Telegram ждёт пустой ответ со статусом 200
        return Response(content="", status_code=200)

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")
    text_lower = text.lower()

    if text_lower.startswith("/start"):
        send_message(
            chat_id,
            f"👋 Привет! Я {BOT_NAME}, твой помощник сайта vibegnews.tilda.ws.\n"
            "Задай вопрос или выбери раздел меню:",
            buttons=MAIN_MENU
        )

    elif text_lower == "история":
        send_message(
            chat_id,
            "Лазурное — уютный поселок на берегу Черного моря в Херсонской области. Основан в 1803 году, известен своими пляжами и гостеприимством.\n\n"
            "В разделе <b>История</b> вы можете узнать интересные исторические факты Причерноморья, прочитать или прослушать на сайте "
            "<a href='https://vibegnews.tilda.ws/'>книги о Лазурном</a>.",
            remove_keyboard=True
        )

    elif text_lower == "домоводство":
        send_message(
            chat_id,
            "В разделе <b>Домоводство</b> вашему вниманию предлагаются практические советы по уюту и эффективности в доме, "
            "рекомендации по экономии семейного бюджета, виноградарству.\n"
            "<b>Например:</b> календарь садовода, как быстро обменять деньги, как выбрать стабилизатор напряжения, "
            "можно ли бороться с растрескиванием ягод винограда.\n"
            "<a href='https://vibegnews.tilda.ws/#rec849880788'>Смотреть раздел Домоводство</a>",
            remove_keyboard=True
        )

    elif text_lower == "it для «чайников»":
        send_message(
            chat_id,
            "В разделе <b>IT для «чайников»</b>: простые и понятные советы по работе с компьютером, смартфоном и интернетом.\n"
            "<b>Например:</b> смартфон для пожилых, статьи по искусственному интеллекту и нейросетям, освоение компьютера.\n"
            "<a href='https://vibegnews.tilda.ws/#rec849898378'>Смотреть IT для «чайников»</a>",
            remove_keyboard=True
        )

    elif text_lower == "faq":
        send_message(
            chat_id,
            "В чате вы можете получить ответы на задаваемые вопросы и воспользоваться помощником "
            "<a href='https://t.me/vibeg52bot'>telegram_bota</a>.\n"
            "<a href='https://vibegnews.tilda.ws/#rec798282698'>FAQ сайта</a>",
            remove_keyboard=True
        )

    elif text_lower == "о боте":
        send_message(
            chat_id,
            "Бот является помощником сайта <a href='https://vibegnews.tilda.ws/'>vibegnews.tilda.ws</a> и даёт ответы по его темам и другим вопросам в его компетенции.",
            remove_keyboard=True
        )

    elif text_lower.startswith("/help") or "помощ" in text_lower:
        send_message(
            chat_id,
            "🆘 Отправь запрос — например: 'как почистить компьютер' или 'настроить Wi-Fi'.\n"
            "Я помогу найти нужную статью.",
            buttons=MAIN_MENU
        )

    elif text_lower.startswith("/about") or "сайт" in text_lower:
        send_message(
            chat_id,
            "🌐 Это бот-помощник проекта <b>VibegNews</b>. "
            "🔗 Посети сайт: https://vibegnews.tilda.ws",
            buttons=MAIN_MENU
        )

    else:
        send_message(
            chat_id,
            f"Я бот {BOT_NAME}. Пожалуйста, выбери раздел из меню или отправь команду /start для возврата меню."
        )

    # КОРРЕКТНЫЙ ОТВЕТ для Telegram!
    return Response(content="", status_code=200)


