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

def save_user_address_via_salebot_api(user_id: str, address: str, api_key: str, project_id: str) -> bool:
    """
    Сохранение адреса пользователя через Salebot API
    согласно документации: https://docs.salebot.pro/api-v-konstruktore-salebot.pro/api-konstruktora
    """
    try:
        # URL для обновления данных пользователя
        url = f"https://api.salebot.pro/api/v1/project/694618/client/update_by_user_id"
        
        # Заголовки согласно документации
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': a0137af5a4ae59eaa087d427dcb0d30e
        }
        
        # Тело запроса согласно документации
        payload = {
            "user_id": user_id,
            "fields": {
                "user_address": address
            }
        }
        
        # Отправляем запрос к Salebot API
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Адрес успешно сохранен через Salebot API для user_id {user_id}")
            return True
        else:
            print(f"❌ Ошибка Salebot API: {response.status_code}, {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при сохранении через Salebot API: {str(e)}")
        return False

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
                'address': address,
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
            
            # Получаем данные пользователя из входящего запроса
            user_id = data.get('user_id') or data.get('userId') or data.get('user', {}).get('id')
            
            # Получаем credentials для Salebot API
            salebot_api_key = data.get('salebot_api_key')
            salebot_project_id = data.get('salebot_project_id')
            
            if user_id and address and salebot_api_key and salebot_project_id:
                try:
                    # Сохраняем адрес через Salebot API
                    save_success = save_user_address_via_salebot_api(
                        user_id=user_id,
                        address=address,
                        api_key=salebot_api_key,
                        project_id=salebot_project_id
                    )
                    
                    if not save_success:
                        print("⚠️ Не удалось сохранить адрес через Salebot API")
                        
                except Exception as e:
                    print(f"❌ Ошибка сохранения адреса: {str(e)}")
            else:
                print("⚠️ Недостаточно данных для сохранения адреса:")
                print(f"   user_id: {user_id}")
                print(f"   address: {address}")
                print(f"   salebot_api_key: {salebot_api_key}")
                print(f"   salebot_project_id: {salebot_project_id}")
            
            return json.dumps({
                'success': True,
                'user_id': user_id,
                'address_saved': bool(user_id and address),
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
    
    # Тест обработки web app данных с Salebot API
    test_web_data = {
        'action': 'process_web_app_data',
        'user_id': '12345',
        'salebot_api_key': 'your_salebot_api_key_here',
        'salebot_project_id': 'your_project_id_here',
        'web_app_data': json.dumps({
            'latitude': 55.7558,
            'longitude': 37.6173,
            'address': 'Москва, Красная площадь'
        }),
        'yandex_api_key': 'test_key'
    }
    result_web = handle(test_web_data)
    print("Тест web app данных:", result_web)