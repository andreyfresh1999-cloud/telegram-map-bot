import requests
import json
import os
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
        
        # Используем прокси Salebot для российских IP
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
                'processed_data': web_app_json
            })
            
        else:
            return json.dumps({
                'success': False,
                'error': 'Unknown action'
            })
            
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': str(e)
        })