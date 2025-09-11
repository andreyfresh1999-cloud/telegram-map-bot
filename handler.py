python
import requests
import json
from typing import Dict, Any

def handle(data: Dict[str, Any]) -> str:
    try:
        action = data.get('action')
        
        if action == 'get_address_from_coords':
            # Простой запрос к Яндекс Геокодеру
            url = "https://geocode-maps.yandex.ru/1.x/"
            params = {
                "apikey": data.get('yandex_api_key', ''),
                "geocode": f"{data.get('longitude', 0)},{data.get('latitude', 0)}",
                "format": "json",
                "lang": "ru_RU",
                "results": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if response.status_code == 200:
                features = result['response']['GeoObjectCollection']['featureMember']
                if features:
                    address = features[0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
                    return json.dumps({
                        'success': True,
                        'address': address,
                        'latitude': data.get('latitude', 0),
                        'longitude': data.get('longitude', 0)
                    })
            
            return json.dumps({'success': False, 'error': 'Адрес не найден'})
            
        return json.dumps({'success': False, 'error': 'Неизвестное действие'})
            
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)})