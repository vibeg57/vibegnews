import requests

# Укажи свои данные:
WEBHOOK_URL = "https://vibegnews.onrender.com/webhook/chat"
WEBHOOK_PASSWORD = "my_super_secret_key_195250"    # замени на фактический пароль

payload = {
    "prompt": "Привет, GPT!",
    "password": WEBHOOK_PASSWORD   # если пароль надо передавать в теле запроса
}
headers = {
    "Content-Type": "application/json"
    # Если пароль требуется в заголовке, раскомментируй и подправь нужную строку:
    # "Authorization": f"Bearer {WEBHOOK_PASSWORD}",
    # "X-Webhook-Password": WEBHOOK_PASSWORD
}

try:
    response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=15)
    print("Статус:", response.status_code)
    print("Ответ:")
    print(response.text)
except Exception as e:
    print("Ошибка запроса:", e)

