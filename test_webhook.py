import requests

WEBHOOK_URL = "https://vibegnews.onrender.com/webhook"

payload = {
    "message": "Привет, бот!"
    # Пароль не нужен, если он не используется в коде обработчика
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=15)
print("Статус:", response.status_code)
print("Ответ:")
print(response.text)
