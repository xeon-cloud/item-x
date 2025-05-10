import requests


def exchangeRate():
    """получаем текущий курс доллара к рублю из апи"""
    try:
        # API ЦБ РФ
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        exchange_rate = data['Valute']['USD']['Value']
        return exchange_rate
    except requests.exceptions.RequestException as e:
        print(f"API Bank Error: {e}")
        return
    except (KeyError, ValueError) as e:
        print(f"API Value Error: {e}")
        return

def convert(amount):
    """конвертируем рубли в доллары по текущему курсу"""
    result = exchangeRate()
    if not result:
        return
    
    return amount / result