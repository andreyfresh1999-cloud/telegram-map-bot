import requests
import json
import logging
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_address_from_yandex(lat: float, lng: float, api_key: str) -> str:
    """Получение адреса через Яндекс Геокодер"""
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": api_key,
            "geocode": f"{lng},{lat}",
            "format": "json",
            "lang": "ru_RU",
            "results": 1
        }
        
        # Прокси для российских IP (если нужно)
        proxies = {
            'http': 'http://139.59.148.123:24532',
            'https': 'http://139.59.148.123:24532'
        }
        
        response = requests.get(url, params=params, proxies=proxies, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            features = data['response']['GeoObjectCollection']['featureMember']
            if features:
                address = features[0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
                logger.info(f"Yandex geocode success: {address}")
                return address
        
        return "Адрес не определен"
            
    except Exception as e:
        logger.error(f"Yandex geocode error: {str(e)}")
        return f"Ошибка определения адреса: {str(e)}"

def handle(data: Dict[str, Any]) -> str:
    """
    Основная функция обработки для Salebot
    Обрабатывает данные из веб-приложения с картой
    """
    try:
        logger.info(f"Received data: {data}")
        
        # Получаем данные из веб-приложения
        web_app_data_str = data.get('webAppData', '{}')
        logger.info(f"Web app data string: {web_app_data_str}")
        
        # Парсим JSON данные
        try:
            web_app_data = json.loads(web_app_data_str)
        except json.JSONDecodeError:
            # Если это не JSON, возможно данные пришли в другой форме
            web_app_data = {}
            if 'latitude' in data:
                web_app_data = {
                    'latitude': float(data.get('latitude', 0)),
                    'longitude': float(data.get('longitude', 0)),
                    'address': data.get('address', ''),
                    'coordinates': data.get('coordinates', '')
                }
        
        # Извлекаем координаты и адрес
        latitude = web_app_data.get('latitude', 0)
        longitude = web_app_data.get('longitude', 0)
        address = web_app_data.get('address', '')
        
        # Если адрес не пришел, пытаемся определить его через Яндекс API
        if not address and latitude != 0 and longitude != 0:
            yandex_api_key = data.get('yandex_api_key', '74752381-5ef1-4dbe-9ecf-9be7281c09f8')
            address = get_address_from_yandex(latitude, longitude, yandex_api_key)
        
        # Формируем результат для Salebot
        result = {
            'success': True,
            'variables': {
                'wibranniy_adres': address,  # Основное поле для формы
                'address': address,          # Дублируем для удобства
                'latitude': latitude,
                'longitude': longitude,
                'coordinates': web_app_data.get('coordinates', f"{latitude:.6f}, {longitude:.6f}"),
                'map_selected': 'true',
                'timestamp': web_app_data.get('timestamp', '')
            },
            'metadata': {
                'source': 'yandex_map',
                'accuracy': 'high'
            }
        }
        
        logger.info(f"Returning result: {result}")
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Error in handle function: {str(e)}"
        logger.error(error_msg)
        
        return json.dumps({
            'success': False,
            'error': error_msg,
            'variables': {
                'wibranniy_adres': 'Ошибка определения адреса',
                'map_selected': 'false',
                'error_occurred': 'true'
            }
        }, ensure_ascii=False)

# Для локального тестирования
if __name__ == "__main__":
    # Тест с данными из веб-приложения
    test_data = {
        'webAppData': json.dumps({
            'latitude': 55.7558,
            'longitude': 37.6173,
            'address': 'Москва, Красная площадь, 1',
            'coordinates': '55.755800, 37.617300',
            'timestamp': '2024-01-15T12:00:00Z'
        }),
        'yandex_api_key': '74752381-5ef1-4dbe-9ecf-9be7281c09f8'
    }
    
    result = handle(test_data)
    print("Тест обработки данных:")
    print(result)