from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
BOT_NAME = "vibegnewsbot"
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


def send_message(chat_id, text, buttons=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if buttons:
        payload["reply_markup"] = {"keyboard": buttons, "resize_keyboard": True}
    requests.post(f"{BASE_URL}/sendMessage", json=payload)


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").lower()

    if text.startswith("/start"):
        send_message(
            chat_id,
            f"👋 Привет! Я {BOT_NAME}, твой помощник сайта vibegnews.tilda.ws.\n"
            "Задай вопрос — я помогу найти нужную статью или дам совет.",
            buttons=[["📰 Советы"], ["ℹ️ Помощь", "📚 О сайте"]],
        )

    elif text.startswith("/help") or "помощ" in text:
        send_message(
            chat_id,
            "🆘 Отправь запрос — например: 'как почистить компьютер' или 'настроить Wi-Fi'.\n"
            "Я найду нужный материал с vibegnews.tilda.ws.",
        )

    elif text.startswith("/about") or "сайт" in text:
        send_message(
            chat_id,
            "🌐 Это бот-помощник проекта <b>VibegNews</b>.\n"
            "🔗 Посети сайт: https://vibegnews.tilda.ws",
        )

    elif "совет" in text or "📰" in text:
        send_message(
            chat_id,
            "📖 Вот полезные материалы:\n"
            "👉 <a href='https://vibegnews.tilda.ws/#rec849880788'>Советы по домоводству</a>\n"
            "👉 <a href='https://vibegnews.tilda.ws/#rec849898378'>Советы IT для «чайников»</a>\n"
            "👉 <a href='https://drive.google.com/file/d/1fSXGoHw7V9sPPg1VLBjzLua4nTqvHSI3/view'>История посёлка Лазурное</a>",
        )

    else:
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "mistral-small-latest",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты помощник сайта vibegnews.tilda.ws. Когда это уместно, вставляй ссылки на статьи с сайта. Используй формат: <a href='URL'>название</a>. Отвечай кратко и по делу.",
                },
                {"role": "user", "content": text},
            ],
        }

        try:
            resp = requests.post(MISTRAL_URL, headers=headers, json=payload)
            result = resp.json()
            answer = result["choices"][0]["message"]["content"]
        except Exception:
            answer = "⚠️ Произошла ошибка при обращении к Mistral AI. Попробуй позже."

        send_message(chat_id, answer)

    return {"ok": True}