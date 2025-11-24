# Варианты заданий для Student 1 (Specification Engineer)

---

## PYTHON + DJANGO API ГРУППА

### Вариант 1: Анализ данных о фильмах (IMDb)

**Датасет**: IMDb Movies Dataset (Kaggle / HuggingFace)

**System Prompt:**
```
You are a data analyst specializing in movie industry trends.
Your task is to create a Django API that analyzes IMDb movie data.

Constraints:
- Use pandas for data processing
- No machine learning models
- API must have 3 endpoints
- Handle missing data gracefully
- Data aggregation only (no individual movie details)

Input format:
- CSV file with columns: title, year, rating, genre, duration, votes
- Genres are comma-separated strings

Output format:
- JSON responses with aggregated statistics
- Include: average_rating, movie_count, min_year, max_year
- Always include HTTP status codes and error messages
```

**Функции для реализации:**
- `get_movies_by_genre(genre: str)` → средний рейтинг, количество фильмов
- `get_top_rated_decades()` → какое десятилетие лучшее по рейтингу
- `get_duration_statistics()` → min, max, average длительность фильма

**Критерии приёмки:**
- ✅ Все 3 endpoint работают без ошибок
- ✅ Обработаны пустые значения в данных
- ✅ Результаты корректные для стандартных запросов
- ✅ API возвращает JSON с нужной структурой

---

### Вариант 2: Анализ продаж в интернет-магазине

**Датасет**: E-commerce Sales Dataset (Kaggle)

**System Prompt:**
```
You are a business analyst for an e-commerce platform.
Your task is to build a Django API for sales data analysis.

Constraints:
- Use pandas for data aggregation
- Time-based filtering required (by date, by month, by year)
- No predictive models
- Must handle CSV with 50k+ rows
- Performance: response time < 2 seconds

Input format:
- CSV: transaction_id, date, product_category, quantity, price, customer_id
- Date format: YYYY-MM-DD
- Price in USD

Output format:
- JSON with metrics: total_revenue, item_count, avg_transaction_value
- Include date range in response
- Status field: success/error
```

**Функции для реализации:**
- `get_sales_by_category(start_date, end_date)` → выручка по категориям
- `get_daily_statistics(date)` → статистика за день
- `get_customer_segments()` → группировка по сумме покупок (VIP/Regular/New)

**Критерии приёмки:**
- ✅ Временные фильтры работают корректно
- ✅ Группировка по категориям правильная
- ✅ Нет дублирования данных в результатах

---

### Вариант 3: Анализ климатических данных

**Датасет**: Global Weather Dataset (OpenWeatherMap / Kaggle)

**System Prompt:**
```
You are an environmental data scientist.
Your task is to create an API for climate data analysis.

Constraints:
- Multiple cities supported
- Monthly and yearly aggregations
- No forecasting models
- Handle incomplete data (missing measurements)
- UTF-8 encoding for city names

Input format:
- CSV: date, city, temperature, humidity, pressure, wind_speed, precipitation
- Date format: YYYY-MM-DD HH:MM:SS
- Temperature in Celsius

Output format:
- JSON: city_name, period, avg_temp, max_temp, min_temp, total_precipitation
- Include data quality metric (% of available measurements)
```

**Функции для реализации:**
- `get_city_statistics(city, year)` → среднегодовые показатели
- `compare_cities(city_list, month)` → сравнение климата между городами
- `find_extreme_days(parameter, limit)` → дни с экстремальными значениями

**Критерии приёмки:**
- ✅ Корректно агрегируют данные за период
- ✅ Сравнение между городами логически верное
- ✅ Обработаны пропущенные значения

---

### Вариант 4: Анализ GitHub репозиториев

**Датасет**: GitHub Archive Dataset или API (HuggingFace Datasets)

**System Prompt:**
```
You are a software metrics analyst.
Your task is to build an API analyzing GitHub repository statistics.

Constraints:
- Analyze: stars, forks, issues, pull_requests, watchers
- Time-based trends (by month/quarter)
- No ML models
- Support multiple languages filter
- Cache results if possible

Input format:
- JSON/CSV: repo_name, language, stars, forks, created_date, updated_date, issues_open, prs_merged
- Date format: ISO 8601

Output format:
- JSON: total_repos, avg_stars, trending_languages, growth_rate
- Include data freshness timestamp
```

**Функции для реализации:**
- `get_trending_repositories(time_period, language)` → самые растущие репо
- `get_language_statistics()` → какой язык популярнее
- `get_repository_health(repo_name)` → метрики здоровья репозитория

**Критерии приёмки:**
- ✅ Тренды рассчитаны правильно
- ✅ Фильтрация по языку работает
- ✅ Результаты актуальны и непротиворечивы

---

### Вариант 5: Анализ музыкальных чартов

**Датасет**: Spotify Top 50 Dataset или Last.fm Charts (Kaggle)

**System Prompt:**
```
You are a music data analyst.
Your task is to create a Django API for music chart analysis.

Constraints:
- Analyze: artist popularity, genre trends, weekly rankings
- Historical data aggregation
- No recommendation system
- Support date range filtering
- Include audio features if available

Input format:
- CSV: track_name, artist, genre, plays, duration, release_date, chart_position, week
- All dates: YYYY-MM-DD
- Plays: integer

Output format:
- JSON: top_artists, popular_genres, avg_plays, trend_direction
- Include period and data points count
```

**Функции для реализации:**
- `get_top_artists(genre, weeks)` → топ артисты за период
- `get_genre_evolution()` → как менялась популярность жанров
- `get_track_statistics(track_name)` → полная статистика трека

**Критерии приёмки:**
- ✅ Ранжирование артистов корректное
- ✅ Тренды жанров рассчитаны верно
- ✅ Обработаны пропуски в датах

---

### Вариант 6: Анализ образовательных данных

**Датасет**: Student Performance Dataset (Kaggle / UCI)

**System Prompt:**
```
You are an educational data analyst.
Your task is to build an API for student performance analysis.

Constraints:
- Analyze across multiple groups/cohorts
- Aggregation by: subject, semester, performance_level
- No predictive modeling
- Handle multiple CSV files (different years)
- Privacy: no individual student names

Input format:
- CSV: student_id, subject, score, attendance, semester, year, difficulty_level
- Score: 0-100, Attendance: 0-100%
- Difficulty levels: beginner, intermediate, advanced

Output format:
- JSON: avg_score, pass_rate, attendance_correlation, subject_comparison
- Include cohort size and statistical significance
```

**Функции для реализации:**
- `get_subject_statistics(year)` → как студенты сдали каждый предмет
- `analyze_attendance_impact()` → корреляция посещаемости и оценок
- `compare_difficulty_levels(subject)` → сравнение успешности по уровням

**Критерии приёмки:**
- ✅ Корреляции вычислены корректно
- ✅ Группировка по предметам полная
- ✅ Нет утечек персональных данных

---

### Вариант 7: Анализ данных о жилищном рынке

**Датасет**: House Prices Dataset (Kaggle / scikit-learn)

**System Prompt:**
```
You are a real estate market analyst.
Your task is to create an API for housing market data analysis.

Constraints:
- Analyze: price trends, location statistics, property features
- Geographic filtering supported
- No price prediction models
- Handle missing data for some features
- Currency: USD

Input format:
- CSV: price, location, bedrooms, bathrooms, square_feet, year_built, sale_date, property_type
- Location: city, state (or coordinates)
- Price in USD, area in sq ft

Output format:
- JSON: avg_price, price_range, avg_size, feature_correlation
- Include market_condition: hot/stable/cold
```

**Функции для реализации:**
- `get_location_statistics(city, property_type)` → средняя цена по локации
- `get_price_distribution()` → диапазон цен и квартили
- `get_feature_statistics()` → как спальни/ванны влияют на цену

**Критерии приёмки:**
- ✅ Цены и площади рассчитаны правильно
- ✅ Геофильтрация точна
- ✅ Корреляции логичны

---

### Вариант 8: Анализ данных авиаполётов

**Датасет**: Flights Dataset (seaborn / Kaggle)

**System Prompt:**
```
You are an aviation data scientist.
Your task is to build an API for flight data analysis.

Constraints:
- Analyze: delays, routes, carriers, seasonal patterns
- Time-based filtering (date, month, year)
- No ML models for prediction
- Handle multiple airports and carriers
- Response time < 1 second

Input format:
- CSV: carrier, flight_number, origin, destination, departure_time, arrival_time, air_time, delay_minutes, distance
- Times in HH:MM format, delay/distance in integers
- Date format: YYYY-MM-DD

Output format:
- JSON: avg_delay, on_time_percentage, most_delayed_routes, delay_by_hour
- Include carrier statistics
```

**Функции для реализации:**
- `get_carrier_statistics(carrier)` → средняя задержка по авиакомпании
- `get_route_analysis(origin, destination)` → анализ конкретного маршрута
- `get_peak_delay_hours()` → в какие часы больше задержек

**Критерии приёмки:**
- ✅ Расчёты задержек верные
- ✅ Статистика по маршрутам полная
- ✅ Временные паттерны рассчитаны

---

### Вариант 9: Анализ данных о преступности

**Датасет**: Crime Dataset (FBI / Kaggle / data.gov)

**System Prompt:**
```
You are a public safety data analyst.
Your task is to create an API for crime statistics analysis.

Constraints:
- Aggregate data by: district, crime_type, time_period
- No individual case details
- Geographic analysis supported
- Privacy-compliant
- Historical trends analysis

Input format:
- CSV: date, district, crime_type, severity, arrests, response_time_minutes
- Date: YYYY-MM-DD
- Crime types: violent, property, drug, other
- Severity: misdemeanor, felony

Output format:
- JSON: crime_count, arrest_rate, severity_distribution, trend_direction
- Include period and district information
```

**Функции для реализации:**
- `get_crime_by_type(time_period)` → какие преступления самые частые
- `get_district_comparison(crime_type)` → где больше преступлений
- `get_arrest_statistics()` → процент арестов по типам

**Критерии приёмки:**
- ✅ Категоризация преступлений верная
- ✅ Статистика по районам полная
- ✅ Тренды рассчитаны корректно

---

### Вариант 10: Анализ данных ресторанов и отзывов

**Датасет**: Restaurants Dataset (Yelp / Kaggle)

**System Prompt:**
```
You are a restaurant industry analyst.
Your task is to build an API for restaurant data analysis.

Constraints:
- Analyze: ratings, reviews, cuisine types, locations
- Sentiment analysis: count positive/negative/neutral reviews
- No NLP models, use simple keyword matching
- Support cuisine and location filtering
- Rating scale 1-5 stars

Input format:
- CSV: restaurant_name, cuisine, location, rating, review_count, avg_review_rating, review_text (optional)
- Rating: 1-5 (float)
- Location: city/state

Output format:
- JSON: avg_rating, top_cuisines, location_statistics, review_sentiment_distribution
- Include restaurant count by criteria
```

**Функции для реализации:**
- `get_top_restaurants(cuisine, location, min_reviews)` → лучшие рестораны
- `get_cuisine_statistics(location)` → средний рейтинг по кухне
- `get_review_sentiment_summary(restaurant_name)` → простой анализ отзывов

**Критерии приёмки:**
- ✅ Фильтрация по кухне и локации работает
- ✅ Рейтинги рассчитаны правильно
- ✅ Анализ тональности отзывов базовый но корректный



---

## Рекомендации для Student 1

### При написании спецификации:
1. **Ясность** - каждое требование должно быть однозначным
2. **Примеры** - покажите примеры входных и выходных данных
3. **Граничные случаи** - упомяните, как обрабатывать пустые данные, null, ошибки
4. **Реальность** - задача должна быть выполнима за 35-40 минут
5. **System Prompt** - напишите как для AI-ассистента, чтобы Student 2 мог скопировать в Cursor

### Типичные ошибки:
- ❌ Слишком сложные требования (не укладываются в 40 минут)
- ❌ Неполные примеры данных
- ❌ Неясные критерии приёмки
- ❌ Забыли обработку ошибок
- ❌ Спецификация для человека, а не для AI

### Время распределение (30 минут):
- 5 мин: Выбор датасета и основной идеи
- 10 мин: Написание System Prompt
- 10 мин: Описание функций и примеров
- 5 мин: Написание критериев приёмки и проверка полноты
