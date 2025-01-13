from flask import Flask, request, jsonify
import re
import requests

# Создаём экземпляр приложения только один раз
app = Flask(__name__)

# Укажите ваш вебхук из Битрикс24
BITRIX24_WEBHOOK_URL = 'https://b24-jxz8u4.bitrix24.ru/rest/1/iqdu9cyh49l0c2xh/crm.lead.add'

# Функция для извлечения данных из сообщения
def parse_message(text):
    pattern = r'Бронирование «(?P<quest_name>.+)» на (?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}) (?P<name>[а-яА-ЯёЁa-zA-Z\s]+) (?P<phone>\+\d{1,3} \(\d{3}\) \d{3}-\d{2}-\d{2}).*Тариф: (?P<people>\d+) человек: (?P<price>\d+) руб.'
    match = re.search(pattern, text)
    return match.groupdict() if match else None

# Функция для отправки данных в Битрикс24
def send_to_bitrix24(data):
    payload = {
        'fields': {
            'TITLE': f"Бронирование: {data['quest_name']}",
            'NAME': data['name'],
            'PHONE': [{'VALUE': data['phone'], 'VALUE_TYPE': 'WORK'}],
            'COMMENTS': f"Дата и время: {data['date']}, Кол-во человек: {data['people']}, Тариф: {data['price']} руб.",
            'SOURCE_ID': 'WEB',
        }
    }
    response = requests.post(BITRIX24_WEBHOOK_URL, json=payload)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if 'message' in data and 'text' in data['message']:
        message_text = data['message']['text']
        parsed_data = parse_message(message_text)

        if parsed_data:
            result = send_to_bitrix24(parsed_data)
            return jsonify(result)

    return jsonify({'status': 'ignored'})

if __name__ == '__main__':
    app.run(port=5000)
