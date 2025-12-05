# Спецификация: Анализ данных авиаполётов

## System Prompt
You are an aviation data scientist. Your task is to build a Django REST API that performs aggregated analysis of historical flight data, focusing on delays, carrier performance, route efficiency, and hourly/seasonal patterns.

**Constraints:**
- Use only data aggregation and filtering (no machine learning or forecasting)
- Support time-based filtering by date, month, and year
- Handle multiple carriers and airport codes correctly
- Ensure every endpoint responds in under 1 second
- All functions must be stateless (no shared memory between requests)

**Input format:**
- A single CSV file with the following columns:
  - `carrier` (str, 2 chars): airline code (e.g., 'AA', 'DL')
  - `flight_number` (int): unique flight identifier
  - `origin` (str, 3 chars): departure airport code (e.g., 'JFK')
  - `destination` (str, 3 chars): arrival airport code
  - `departure_time`, `arrival_time` (str): time in `HH:MM` format
  - `air_time` (int): flight duration in minutes
  - `delay_minutes` (int): departure delay in minutes (negative = early)
  - `distance` (int): flight distance in miles
- If temporal filtering is needed, a separate `date` column in `YYYY-MM-DD` format is assumed to exist or be joinable

**Output format:**
- JSON responses containing only aggregated metrics
- Must include: `avg_delay`, `on_time_percentage`, `most_delayed_routes`, `delay_by_hour`
- Include error messages and proper HTTP status codes (e.g., 400 for invalid input, 404 for missing route)

---

## Данные

**Источник датасета:**
- Primary: [Kaggle – Flight Delays Dataset](https://www.kaggle.com/datasets/usdot/flight-delays)
- Fallback for demo: `seaborn.load_dataset('flights')` (limited fields, for testing only)

**Размер датасета:**
- ~584,000 rows
- 9 core columns (as listed above)

**Описание полей:**

| Поле              | Тип     | Описание                                      |
|-------------------|---------|-----------------------------------------------|
| `carrier`         | string  | Код авиакомпании (2 символа)                  |
| `flight_number`   | integer | Номер рейса                                   |
| `origin`          | string  | Аэропорт вылета (3 символа, напр. JFK)        |
| `destination`     | string  | Аэропорт прибытия (3 символа)                 |
| `departure_time`  | string  | Время вылета в формате `HH:MM`                |
| `arrival_time`    | string  | Время прилёта в формате `HH:MM`               |
| `air_time`        | integer | Продолжительность полёта (минуты)             |
| `delay_minutes`   | integer | Задержка вылета (минуты; может быть отрицательной) |
| `distance`        | integer | Расстояние между аэропортами (в милях)        |

**Примеры данных:**

```csv

carrier,flight_number,origin,destination,departure_time,arrival_time,air_time,delay_minutes,distance
AA,2154,JFK,LAX,08:15,11:45,205,15,2475
DL,1421,ATL,SFO,06:30,09:15,225,-5,2139
UA,731,ORD,DFW,10:45,13:20,155,22,802
WN,1254,LAX,PHX,14:20,15:45,85,8,370

```
---

## Функциональные требования

### Функция 1: `get_carrier_statistics(carrier: str)`
Возвращает агрегированную статистику по выбранной авиакомпании.

**Параметры:**
- `carrier` (str): код авиакомпании, например `'AA'`

**Ожидаемый результат (JSON):**
```json
{
  "carrier": "AA",
  "avg_delay": 12.5,
  "on_time_percentage": 78.3,
  "total_flights": 15420,
  "most_common_routes": [
    {"route": "JFK-LAX", "flights": 542},
    {"route": "ORD-DFW", "flights": 487}
  ],
  "delay_by_month": {
    "1": 15.2,
    "2": 12.1,
    "12": 18.5
  }
}
```
---

### Функция 2: get_route_analysis(origin, destination)
Предоставляет детальную сводку по заданному авиамаршруту между двумя аэропортами.

**Входные параметры:**

- `origin` (str): трёхбуквенный код аэропорта отправления (например, 'JFK')
- `destination` (str): трёхбуквенный код аэропорта прибытия (например, 'LAX')
**Ожидаемый результат:**
```json

{
    "route": "JFK-LAX",
    "avg_delay": 14.2,
    "on_time_percentage": 75.8,
    "carriers_on_route": [
        {"carrier": "AA", "flights": 254, "avg_delay": 12.1},
        {"carrier": "DL", "flights": 187, "avg_delay": 16.3}
    ],
    "best_time_to_fly": {
        "hour": 8,
        "avg_delay": 6.2
    },
    "distance": 2475
}
```

### Функция 3: get_peak_delay_hours()
Определяет часы суток с наибольшими и наименьшими задержками вылетов на основе всего доступного набора данных.

**Входные параметры:**
— отсутствуют

**Ожидаемый результат:**
```json
{
  "delay_by_hour": {
    "5": 5.8,
    "6": 5.2,
    "17": 18.7,
    "18": 22.4,
    "19": 20.1,
    "23": 15.8
  },
  "peak_delay_hours": [
    {"hour": 18, "avg_delay": 22.4},
    {"hour": 19, "avg_delay": 20.1},
    {"hour": 17, "avg_delay": 18.7}
  ],
  "best_hours": [
    {"hour": 6, "avg_delay": 5.2},
    {"hour": 5, "avg_delay": 5.8}
  ]
}
```

### Дополнительные функции

#### g`et_seasonal_patterns(year: int = None)`
Позволяет изучить, как задержки рейсов зависят от времени года. Если указан год — анализ проводится только за этот период; если не указан — используется весь доступный временной охват.

#### `filter_flights_by_date(start_date: str, end_date: str)`
Возвращает подмножество рейсов, попадающих в заданный интервал дат (включительно). Формат дат: YYYY-MM-DD.

### Примеры использования

```python
# Получение общей статистики по авиакомпании
stats = get_carrier_statistics('AA')
print(f"Авиакомпания AA: {stats['on_time_percentage']}% рейсов выполняются без опозданий")

# Анализ маршрута между аэропортами JFK и LAX
route_data = get_route_analysis('JFK', 'LAX')
optimal_hour = route_data['best_time_to_fly']['hour']
print(f"Оптимальное время вылета на маршруте JFK–LAX: {optimal_hour}:00")

# Определение часов с наибольшими задержками
delay_stats = get_peak_delay_hours()
peak_list = [entry['hour'] for entry in delay_stats['peak_delay_hours'][:3]]
print(f"Часы с максимальными задержками: {peak_list}")
```

## Ограничения и условия

### Используемые библиотеки
```python
import pandas as pd
import numpy as np
from datetime import datetime
import json
from typing import Dict, List, Optional
```

### Запретные операции
- Применение моделей машинного обучения или предсказательной аналитики
- Изменение исходного датасета (разрешён только read-only анализ)
- Сохранение состояния между вызовами функций (все функции должны быть stateless)

### Обработка граничных случаев

```python
# Обработка отсутствующих данных
def handle_missing_data(df):
    # Заполнение пропущенных задержек нулями
    df['delay_minutes'] = df['delay_minutes'].fillna(0)
    return df

# Валидация входных параметров
def validate_airport_code(code):
    if not code or len(code) != 3:
        raise ValueError("Код аэропорта должен состоять из 3 символов")

# Обработка несуществующих маршрутов
def check_route_exists(origin, destination):
    route_flights = df[(df['origin'] == origin) & (df['destination'] == destination)]
    if len(route_flights) == 0:
        return {"error": "Маршрут не найден"}
```

### Требования к производительности
- Время ответа на любой запрос должно быть менее 1 секунды.
- Система должна выдерживать нагрузку до 1000 параллельных запросов.
- Рекомендуется использовать кэширование для часто запрашиваемых маршрутов или авиакомпаний.
- Все операции над данными должны быть оптимизированы (избегать неэффективных циклов, использовать векторизацию через pandas).

## Критерии приёмки

### Проверочный список

#### ✅ Корректность расчётов задержек
- [ ] Среднее значение задержки учитывает как положительные, так и отрицательные значения
- [ ] Процент своевременных рейсов (delay_minutes <= 0) вычисляется верно
- [ ] Ранние вылеты (отрицательные задержки) не искажают статистику
#### ✅ Полнота информации по маршрутам
- [ ] Все рейсы на заданном направлении учитываются при агрегации
- [ ] Для каждого маршрута перечислены все авиакомпании, выполняющие перелёты
- [ ] Расстояние и временные метрики соответствуют реальным данным
#### ✅ Работа с временными паттернами
- [ ] Агрегация по часам суток (departure_time → hour) реализована корректно
- [ ] Сезонные тенденции (если реализованы) основаны на месяцах или кварталах
- [ ] Фильтрация по датам (если реализована) работает без ошибок

### Примеры успешного выполнения

```python
# Тест 1: Проверка структуры ответа для авиакомпании
res = get_carrier_statistics('UA')
assert 'avg_delay' in res
assert 0 <= res['on_time_percentage'] <= 100

# Тест 2: Проверка существования рейсов на маршруте
res = get_route_analysis('JFK', 'LAX')
assert len(res['carriers_on_route']) > 0

# Тест 3: Проверка производительности
import time
start = time.time()
get_peak_delay_hours()
assert time.time() - start < 1.0
```

### Ожидаемые метрики качества

- **Точность расчётов:** не ниже 99.9%
- **Полнота охвата:** все доступные маршруты и авиакомпании включены в анализ
- **Время отклика:** менее 1 секунды на любой валидный запрос
- **Надёжность API:** доступность не ниже 99.9% в штатном режиме