# VibegBot — Telegram бот-помощник для vibegnews.tilda.ws

## 🔧 Настройка
1. Создай Telegram-бота через [@BotFather](https://t.me/BotFather)
2. Скопируй токен → вставь в Render переменную `TELEGRAM_TOKEN`
3. Получи API-ключ на [console.mistral.ai](https://console.mistral.ai) → вставь в Render `MISTRAL_API_KEY`

## 🚀 Развёртывание на Render
1. Создай репозиторий с этими файлами на GitHub  
2. Перейди в [Render Dashboard](https://render.com) → **New → Web Service**  
3. Подключи GitHub, выбери ветку с ботом  
4. Укажи:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance type:** Free  
5. После деплоя Render даст URL, например:  
   `https://vibeg-bot.onrender.com/webhook`

6. Установи вебхук для Telegram:
   ```
   https://api.telegram.org/bot<ТВОЙ_ТОКЕН>/setWebhook?url=https://vibeg-bot.onrender.com/webhook
   ```

7. Напиши `/start` в Telegram — бот заработает 🎉
