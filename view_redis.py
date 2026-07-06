import redis
import os
import json
from dotenv import load_dotenv

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def main():
    print(f"Подключение к Redis по адресу: {REDIS_URL}")
    
    try:
        
        r = redis.from_url(REDIS_URL, decode_responses=True)
        
        
        keys = r.keys("order:*")
        if not keys:
            print("В кэше Redis нет сохраненных заказов. Сначала оформите заказ на сайте!")
            return
            
        print(f"Найдено заказов в кэше: {len(keys)}")
        print("=" * 60)
        
        
        for key in sorted(keys):
            val = r.get(key)
            try:
                data = json.loads(val)
                print(f"Ключ: {key}")
                print(f"  Пользователь: {data.get('username')}")
                print(f"  Номер заказа: {data.get('order_number')}")
                print(f"  Время заказа: {data.get('created_at')}")
                print("  Позиции заказа:")
                for item in data.get('items', []):
                    print(f"    * {item.get('name')} x{item.get('amount')} ({item.get('price')} Р)")
            except Exception as e:
                print(f"Ключ: {key} (Сырые данные): {val}")
            print("-" * 60)
            
    except Exception as e:
        print(f"Ошибка подключения к Redis: {e}")
        print("Убедитесь, что Redis-сервер запущен.")

if __name__ == "__main__":
    main()
