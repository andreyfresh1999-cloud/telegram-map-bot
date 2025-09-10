import requests
import json
from typing import Dict, Any

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
        
        # Прокси для российских IP
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
                return address
        
        return "Адрес не определен"
            
    except Exception as e:
        return f"Ошибка определения адреса: {str(e)}"

def handle(data: Dict[str, Any]) -> str:
    """
    Основная функция обработки для Salebot
    """
    try:
        action = data.get('action')
        
        if action == 'get_address_from_coords':
            # Получение адреса по координатам
            latitude = float(data.get('latitude', 0))
            longitude = float(data.get('longitude', 0))
            api_key = data.get('yandex_api_key', '')
            
            # Получаем адрес из координатов
            address = get_address_from_yandex(latitude, longitude, api_key)
            
            return json.dumps({
                'success': True,
                'address': address,  # Возвращаем АДРЕС, а не координаты
                'latitude': latitude,
                'longitude': longitude,
                'coordinates': f"{latitude:.6f}, {longitude:.6f}"
            })
            
        elif action == 'process_web_app_data':
            # Обработка данных из веб-приложения
            web_app_data = data.get('web_app_data', '{}')
            web_app_json = json.loads(web_app_data)
            
            # Если веб-приложение уже прислало адрес, используем его
            address = web_app_json.get('address', '')
            
            # Если адреса нет, пытаемся определить его из координатов
            if not address and 'latitude' in web_app_json and 'longitude' in web_app_json:
                api_key = data.get('yandex_api_key', '')
                address = get_address_from_yandex(
                    web_app_json['latitude'], 
                    web_app_json['longitude'], 
                    api_key
                )
            
            return json.dumps({
                'success': True,
                'processed_data': {
                    'address': address,
                    'latitude': web_app_json.get('latitude', 0),
                    'longitude': web_app_json.get('longitude', 0),
                    'coordinates': web_app_json.get('coordinates', '')
                }
            })
            
        elif action == 'test':
            # Тестовая функция
            return json.dumps({
                'success': True,
                'message': 'Handler работает! Возвращает адреса.',
                'received_data': data
            })
            
        else:
            return json.dumps({
                'success': False,
                'error': 'Unknown action',
                'action': action
            })
            
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })

# Для локального тестирования
if __name__ == "__main__":
    # Тест определения адреса
    test_data = {
        'action': 'get_address_from_coords',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'yandex_api_key': 'test_key'
    }
    result = handle(test_data)
    print("Тест определения адреса:", result)
    
    # Тест обработки web app данных
    test_web_data = {
        'action': 'process_web_app_data',
        'web_app_data': json.dumps({
            'latitude': 55.7558,
            'longitude': 37.6173,
            'address': 'Москва, Красная площадь'
        }),
        'yandex_api_key': 'test_key'
    }
    result_web = handle(test_web_data)
    print("Тест web app данных:", result_web)