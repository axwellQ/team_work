from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict, List
from functools import lru_cache

application = FastAPI(title="Анализ данных авиарейсов API")

# ---------- Загрузка и обработка данных ----------
# Ожидается файл CSV с колонками:
# carrier,flight_number,origin,destination,departure_time,arrival_time,air_time,delay_minutes,distance,date
# date в формате ГГГГ-ММ-ДД
# Для тестирования загружаем из файла flights.csv в текущей папке.
# В реальном проекте можно поменять путь или источник.
FILE_PATH = "flights.csv"


def load_dataset(file_path=FILE_PATH) -> pd.DataFrame:
    data_frame = pd.read_csv(
        file_path,
        dtype={
            "carrier": str,
            "flight_number": int,
            "origin": str,
            "destination": str,
            "departure_time": str,
            "arrival_time": str,
            "air_time": float,
            "delay_minutes": float,
            "distance": float,
            "date": str,
        },
    )

    # Приводим к верхнему регистру и убираем пробелы
    data_frame["carrier"] = data_frame["carrier"].str.upper().str.strip()
    data_frame["origin"] = data_frame["origin"].str.upper().str.strip()
    data_frame["destination"] = data_frame["destination"].str.upper().str.strip()

    # Заполняем пропуски в задержках нулями
    data_frame["delay_minutes"] = data_frame["delay_minutes"].fillna(0).astype(float)

    # Преобразуем дату
    data_frame["date"] = pd.to_datetime(data_frame["date"], format="%Y-%m-%d", errors="coerce")

    # Удаляем строки без даты
    data_frame = data_frame[~data_frame["date"].isna()].copy()

    # Добавляем вспомогательные колонки
    data_frame["month"] = data_frame["date"].dt.month
    data_frame["year"] = data_frame["date"].dt.year

    # Получаем час вылета из времени
    def extract_hour(time_str):
        try:
            return int(str(time_str).split(":")[0])
        except Exception:
            return np.nan

    data_frame["departure_hour"] = (
        data_frame["departure_time"].apply(extract_hour).fillna(-1).astype(int)
    )

    # Создаем маршрут
    data_frame["route"] = data_frame["origin"] + "-" + data_frame["destination"]

    return data_frame


# Загружаем данные в память (разрешено для ~584k строк)
flight_data = load_dataset()


# ---------- Вспомогательные функции ----------
def check_airport_code(airport_code: str):
    if not airport_code or len(airport_code) != 3:
        raise HTTPException(
            status_code=400,
            detail="Код аэропорта должен содержать 3 символа",
        )


def check_carrier_code(carrier_code: str):
    if not carrier_code or len(carrier_code) not in (2, 3):
        raise HTTPException(status_code=400, detail="Некорректный код авиакомпании")


def process_missing_values(df_local: pd.DataFrame) -> pd.DataFrame:
    df_local = df_local.copy()
    df_local["delay_minutes"] = df_local["delay_minutes"].fillna(0)
    return df_local


# Кэш для часто запрашиваемых агрегаций
@lru_cache(maxsize=1024)
def get_cached_aggregation(func_name: str, parameters: str):
    return None


# ---------- Модели ответов ----------
class AirlineStatsResponse(BaseModel):
    carrier: str
    avg_delay: float
    on_time_percentage: float
    total_flights: int
    most_common_routes: List[Dict[str, int]]
    delay_by_month: Dict[str, float]


class RouteStatsResponse(BaseModel):
    route: str
    avg_delay: float
    on_time_percentage: float
    carriers_on_route: List[Dict]
    best_time_to_fly: Dict
    distance: Optional[float]


class DelayHoursResponse(BaseModel):
    delay_by_hour: Dict[str, float]
    peak_delay_hours: List[Dict]
    best_hours: List[Dict]


# ---------- Основные вычисления ----------
def calculate_punctuality(series: pd.Series) -> float:
    # "Вовремя" — задержка ≤ 0 (включая отрицательные значения)
    total_count = len(series)
    if total_count == 0:
        return 0.0
    on_time_count = (series <= 0).sum()
    return round((on_time_count / total_count) * 100, 2)


def calculate_mean_safely(series: pd.Series) -> float:
    if len(series) == 0:
        return 0.0
    return float(round(series.mean(), 2))


# ---------- Конечные точки API ----------


@application.get("/carrier/{carrier}", response_model=AirlineStatsResponse)
def get_carrier_info(
        carrier: str,
        year: Optional[int] = Query(None),
        month: Optional[int] = Query(None),
):
    carrier = carrier.upper()
    check_carrier_code(carrier)

    # Фильтруем по авиакомпании и времени
    filtered_df = flight_data[flight_data["carrier"] == carrier]
    if year:
        filtered_df = filtered_df[filtered_df["year"] == int(year)]
    if month:
        filtered_df = filtered_df[filtered_df["month"] == int(month)]

    if filtered_df.empty:
        raise HTTPException(
            status_code=404, detail="Авиакомпания или данные не найдены"
        )

    filtered_df = process_missing_values(filtered_df)
    average_delay = calculate_mean_safely(filtered_df["delay_minutes"])
    punctuality_rate = calculate_punctuality(filtered_df["delay_minutes"])
    flight_count = len(filtered_df)

    # Популярные маршруты
    route_counts = filtered_df.groupby("route").size().sort_values(ascending=False).head(10)
    common_routes = [
        {"route": route_name, "flights": int(count)} for route_name, count in route_counts.items()
    ]

    # Задержка по месяцам
    monthly_delays = (
        filtered_df.groupby("month")["delay_minutes"].mean().round(2).to_dict()
    )

    # Преобразуем ключи в строки
    monthly_delay_dict = {
        str(int(key)): float(value) for key, value in monthly_delays.items()
    }

    return {
        "carrier": carrier,
        "avg_delay": float(average_delay),
        "on_time_percentage": float(punctuality_rate),
        "total_flights": int(flight_count),
        "most_common_routes": common_routes,
        "delay_by_month": monthly_delay_dict,
    }


@application.get("/route/{origin}/{destination}", response_model=RouteStatsResponse)
def analyze_route(
        origin: str,
        destination: str,
        year: Optional[int] = Query(None),
        month: Optional[int] = Query(None),
):
    origin = origin.upper()
    destination = destination.upper()
    check_airport_code(origin)
    check_airport_code(destination)

    filtered_df = flight_data[(flight_data["origin"] == origin) & (flight_data["destination"] == destination)]
    if year:
        filtered_df = filtered_df[filtered_df["year"] == int(year)]
    if month:
        filtered_df = filtered_df[filtered_df["month"] == int(month)]

    if filtered_df.empty:
        raise HTTPException(status_code=404, detail="Маршрут не найден")

    filtered_df = process_missing_values(filtered_df)
    average_delay = calculate_mean_safely(filtered_df["delay_minutes"])
    punctuality_rate = calculate_punctuality(filtered_df["delay_minutes"])

    # Авиакомпании на маршруте
    carrier_stats = (
        filtered_df.groupby("carrier")
        .agg(total_flights=("carrier", "size"), mean_delay=("delay_minutes", "mean"))
        .reset_index()
        .sort_values(by="total_flights", ascending=False)
    )

    carriers_on_path = [
        {
            "carrier": row["carrier"],
            "flights": int(row["total_flights"]),
            "avg_delay": float(round(row["mean_delay"], 2)),
        }
        for _, row in carrier_stats.iterrows()
    ]

    # Лучшее время для вылета
    hour_groups = (
        filtered_df[filtered_df["departure_hour"] >= 0].groupby("departure_hour")["delay_minutes"].mean()
    )

    if not hour_groups.empty:
        optimal_hour = int(hour_groups.idxmin())
        optimal_delay = float(round(hour_groups.min(), 2))
    else:
        optimal_hour = None
        optimal_delay = 0.0

    # Расстояние
    route_distance = (
        float(filtered_df["distance"].median()) if "distance" in filtered_df.columns else None
    )

    return {
        "route": f"{origin}-{destination}",
        "avg_delay": float(average_delay),
        "on_time_percentage": float(punctuality_rate),
        "carriers_on_route": carriers_on_path,
        "best_time_to_fly": {"hour": optimal_hour, "avg_delay": optimal_delay},
        "distance": route_distance,
    }


@application.get("/peak_delay_hours", response_model=DelayHoursResponse)
def get_delay_by_hour(
        year: Optional[int] = Query(None), month: Optional[int] = Query(None)
):
    filtered_df = flight_data
    if year:
        filtered_df = filtered_df[filtered_df["year"] == int(year)]
    if month:
        filtered_df = filtered_df[filtered_df["month"] == int(month)]

    filtered_df = process_missing_values(filtered_df)

    # Группируем по часам (0-23)
    hourly_avg = (
        filtered_df[filtered_df["departure_hour"] >= 0]
        .groupby("departure_hour")["delay_minutes"]
        .mean()
        .reindex(range(0, 24))
        .fillna(0)
        .round(2)
    )

    delay_per_hour = {str(int(hour)): float(delay) for hour, delay in hourly_avg.items()}

    # Часы с наибольшими задержками
    top_delays = hourly_avg.sort_values(ascending=False).head(5)
    peak_hours = [
        {"hour": int(hour), "avg_delay": float(round(delay, 2))}
        for hour, delay in zip(top_delays.index, top_delays.values)
    ]

    # Часы с наименьшими задержками
    best_times = hourly_avg.sort_values(ascending=True).head(5)
    best_hours_list = [
        {"hour": int(hour), "avg_delay": float(round(delay, 2))}
        for hour, delay in zip(best_times.index, best_times.values)
    ]

    return {
        "delay_by_hour": delay_per_hour,
        "peak_delay_hours": peak_hours,
        "best_hours": best_hours_list,
    }


# Дополнительные конечные точки


@application.get("/seasonal_patterns")
def analyze_seasonal_patterns(year: Optional[int] = Query(None)):
    filtered_df = flight_data
    if year:
        filtered_df = filtered_df[filtered_df["year"] == int(year)]

    filtered_df = process_missing_values(filtered_df)

    # Статистика по месяцам
    monthly_stats = (
        filtered_df.groupby("month")["delay_minutes"]
        .agg(["mean", "count", "median"])
        .round(2)
    )

    patterns = {
        str(int(month_num)): {
            "avg_delay": float(row["mean"]),
            "median_delay": float(row["median"]),
            "flights": int(row["count"]),
        }
        for month_num, row in monthly_stats.iterrows()
    }

    return {"year": int(year) if year else None, "monthly_patterns": patterns}


@application.get("/filter_by_date")
def filter_by_date_range(
        start_date: str = Query(...),
        end_date: str = Query(...),
        limit: int = Query(100),
):
    # Проверяем даты
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except Exception:
        raise HTTPException(
            status_code=400, detail="Даты должны быть в формате ГГГГ-ММ-ДД"
        )

    if start_dt > end_dt:
        raise HTTPException(
            status_code=400, detail="Дата начала не может быть позже даты окончания"
        )

    mask = (flight_data["date"] >= start_dt) & (flight_data["date"] <= end_dt)
    filtered_df = flight_data.loc[mask].head(limit)

    # Преобразуем в список словарей
    flight_records = filtered_df[
        [
            "carrier",
            "flight_number",
            "origin",
            "destination",
            "departure_time",
            "arrival_time",
            "air_time",
            "delay_minutes",
            "distance",
            "date",
        ]
    ].to_dict(orient="records")

    # Преобразуем даты в строки
    for record in flight_records:
        record["date"] = record["date"].strftime("%Y-%m-%d")

    return {
        "start_date": start_date,
        "end_date": end_date,
        "count": len(flight_records),
        "flights": flight_records,
    }


# ---------- Проверка работы ----------
@application.get("/health")
def check_health():
    return {"status": "готов", "rows": len(flight_data)}

# ---------- Заметки о производительности ----------
# - Данные загружаются в память (ответы <1s для ~584k строк)
# - Для высоких нагрузок рекомендуется: Redis/fast-cache, предвычисленные агрегаты, Dask/Polars или колоночные хранилища
# - lru_cache можно применять для часто запрашиваемых агрегаций