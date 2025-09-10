import requests
import json
import os
from typing import Dict, Any

def get_address_from_yandex(lat: float, lng: float, api_key: str) -> str:
    """Получение адреса через Яндекс Геокодер"""
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": AQVN3PPHRO_V9BVXewsyJQ00foVcabytG0PjfTCp,
            "geocode": f"{lng},{lat}",
            "format": "json",
            "lang": "ru_RU",
            "results": 1
        }
        
        # Используем прокси Salebot для российских IP - executor кода для Python
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
    data: словарь с параметрами из блока
    """
    try:
        # Получаем тип действия из параметров
        action = data.get('action')
        
        if action == 'get_address_from_coords':
            # Получение адреса по координатам
            latitude = float(data.get('latitude', 0))
            longitude = float(data.get('longitude', 0))
            api_key = data.get('yandex_api_key', '')
            
            address = get_address_from_yandex(latitude, longitude, api_key)
            
            return json.dumps({
                'success': True,
                'address': address,
                'latitude': latitude,
                'longitude': longitude
            })
            
        elif action == 'process_web_app_data':
            # Обработка данных из веб-приложения
            web_app_data = data.get('web_app_data', '{}')
            web_app_json = json.loads(web_app_data)
            
            return json.dumps({
                'success': True,
                'processed_data': web_app_json,
                'action': 'web_app_processed'
            })
            
        elif action == 'test_connection':
            # Тестовый запрос для проверки соединения
            test_url = "https://geocode-maps.yandex.ru/1.x/"
            proxies = {
                'http': 'http://139.59.148.123:24532',
                'https': 'http://139.59.148.123:24532'
            }
            
            test_response = requests.get(test_url, proxies=proxies, timeout=5)
            
            return json.dumps({
                'success': True,
                'status_code': test_response.status_code,
                'message': 'Connection test successful'
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
            'error': str(e),
            'proxy_used': '139.59.148.123:24532'
        })

# Для локального тестирования
if __name__ == "__main__":
    # Тестовые данные
    test_data = {
        'action': 'get_address_from_coords',
        'latitude': 55.7558,
        'longitude': 37.6173,
        'yandex_api_key': 'your_test_key'
    }
    
    result = handle(test_data)
    print("Result:", result)
    
    # Тест соединения
    test_connection = {
        'action': 'test_connection'
    }
    
    connection_result = handle(test_connection)
    print("Connection test:", connection_result)