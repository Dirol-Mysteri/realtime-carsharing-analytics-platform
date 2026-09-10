import time
import random
import uuid
from datetime import datetime, timezone
import clickhouse_connect

import config

# Подключение к нашему ClickHouse в Docker
client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username=config.CH_USER,
    password=config.CH_PASS,
    database=config.CH_DB
)

# --- SENIOR APPROACH: Автоматическое создание RAW-таблицы при старте ---
print("🔧 Проверяем и создаем инфраструктуру для сырых данных...")
client.command("""
CREATE TABLE IF NOT EXISTS carsharing_raw.car_telemetry (
    car_id UUID,
    user_id UUID,
    trip_id UUID,
    timestamp DateTime64(3, 'UTC'),
    latitude Float64,
    longitude Float64,
    speed Float32,
    fuel_level_percent UInt8,
    status String
) ENGINE = MergeTree()
ORDER BY (status, timestamp);
""")
print("✅ Таблица car_telemetry готова к приему данных.")

# Генерируем пул из 10 фейковых машин
CARS = [uuid.uuid4() for _ in range(10)]
active_trips = {}

print("🚀 Генератор запущен. Начинаем стриминг данных в ClickHouse...")

try:
    while True:
        data_to_insert = []
        
        for car_id in CARS:
            # 20% шанс, что машина изменит статус (начнет поездку)
            if car_id not in active_trips and random.random() < 0.2:
                active_trips[car_id] = {
                    'user_id': uuid.uuid4(),
                    'trip_id': uuid.uuid4(),
                    'lat': random.uniform(55.55874, 55.91428), 
                    'lon': random.uniform(37.36932, 37.84650),
                    'fuel': random.randint(50, 100)
                }
            
            if car_id in active_trips:
                trip = active_trips[car_id]
                
                trip['lat'] += random.uniform(-0.001, 0.001)
                trip['lon'] += random.uniform(-0.001, 0.001)
                # Топливо уменьшается с каждым тиком
                trip['fuel'] = max(0, trip['fuel'] - random.randint(0, 2)) 
                
                status = 'in_progress'
                
                # Шанс 10% завершить поездку или если кончилось топливо
                if random.random() < 0.1 or trip['fuel'] == 0:
                    status = 'finished'
                    
                row = [
                    car_id,
                    trip['user_id'],
                    trip['trip_id'],
                    datetime.now(timezone.utc),
                    trip['lat'],
                    trip['lon'],
                    float(random.randint(10, 80) if status == 'in_progress' else 0),
                    int(trip['fuel']),
                    status
                ]
                data_to_insert.append(row)
                
                if status == 'finished':
                    del active_trips[car_id]
            else:
                # Машина стоит на парковке
                if random.random() < 0.05: 
                    row = [
                        car_id,
                        None,
                        None,
                        datetime.now(timezone.utc),
                        random.uniform(55.55874, 55.91428),
                        random.uniform(37.36932, 37.84650),
                        0.0,
                        random.randint(20, 100),
                        'parked'
                    ]
                    data_to_insert.append(row)

        if data_to_insert:
            client.insert(
                'car_telemetry', 
                data_to_insert, 
                column_names=['car_id', 'user_id', 'trip_id', 'timestamp', 'latitude', 'longitude', 'speed', 'fuel_level_percent', 'status']
            )
            print(f"📥 Записано строк: {len(data_to_insert)} | Активных поездок: {len(active_trips)}")
            
        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 Генератор остановлен.")
