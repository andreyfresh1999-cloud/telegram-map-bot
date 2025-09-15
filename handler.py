import json
import requests
from logger import logger

def handle(data):
    """
    Обработчик данных из веб-приложения с картой для SaleBot
    """
    try:
        logger.info(f"Received data: {data}")
        
        # Получаем данные из веб-приложения
        webapp_data = data.get('webapp_data', '{}')
        location_data = json.loads(webapp_data)
        
        # Извлекаем данные о местоположении
        address = location_data.get('address', 'Адрес не указан')
        latitude = location_data.get('latitude', 0)
        longitude = location_data.get('longitude', 0)
        coordinates = location_data.get('coordinates', '0, 0')
        user_id = location_data.get('user_id', '')
        
        # Валидация данных
        if not address or address == 'Адрес не указан':
            return json.dumps({
                'success': False,
                'error': 'No address selected',
                'message': '❌ Пожалуйста, выберите адрес на карте'
            })
        
        # Логируем успешное получение данных
        logger.info(f"User {user_id} selected address: {address}")
        
        # Возвращаем данные для использования в боте
        return json.dumps({
            'success': True,
            'selected_address': address,
            'selected_latitude': latitude,
            'selected_longitude': longitude,
            'selected_coordinates': coordinates,
            'user_id': user_id,
            'message': f'✅ Отлично! Вы выбрали точку:\n\n📍 {address}\n🌐 Координаты: {coordinates}'
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return json.dumps({
            'success': False,
            'error': 'Invalid JSON format',
            'message': '❌ Ошибка обработки данных'
        })
        
    except Exception as e:
        logger.error(f"Error processing location data: {str(e)}")
        return json.dumps({
            'success': False,
            'error': str(e),
            'message': '❌ Произошла ошибка при обработке выбранной точки'
        })

# Для тестирования
if __name__ == "__main__":
    test_data = {
        'webapp_data': '{"address":"Москва, Красная площадь","latitude":55.7539,"longitude":37.6208,"coordinates":"55.7539, 37.6208","user_id":12345}'
    }
    result = handle(test_data)
    print("Test result:", result)