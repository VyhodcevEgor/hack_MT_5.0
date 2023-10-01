from Database.settings import user, password, host, db_name, yandex_api_key
from Database.database_requests import (
    insert_bank_info,
    insert_availabilities,
    select_all_bank_info,
    insert_average_load
)
from random import sample, randint, choice
from pprint import pprint
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
)
import requests
import datetime

engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8mb4"
)


def add_times(time1, time2):
    total_minutes = (time1.hour * 60 + time1.minute) + (time2.hour * 60 + time2.minute)
    result_time = datetime.time(total_minutes // 60, total_minutes % 60)
    return result_time


def load_by_time(hour):
    load = {
        0: [0, 5],
        1: [0, 5],
        2: [0, 5],
        3: [0, 5],
        4: [0, 5],
        5: [0, 5],
        6: [10, 20],
        7: [20, 40],
        8: [30, 50],
        9: [20, 40],
        10: [15, 30],
        11: [10, 25],
        12: [10, 25],
        13: [10, 25],
        14: [10, 25],
        15: [20, 40],
        16: [30, 50],
        17: [40, 60],
        18: [15, 30],
        19: [5, 25],
        20: [5, 15],
        21: [0, 15],
        22: [0, 10],
        23: [0, 5],
    }
    return randint(load[hour][0], load[hour][1])


def calculate_spn(radius_meters):
    meters_per_degree_lat = 111320.0
    lat_span = radius_meters / meters_per_degree_lat
    lon_span = lat_span
    return lat_span, lon_span


def map_search_yandex(lat, lng, query, radius, skip=0, types=0):
    """
    :param lat:
    :param lng:
    :param query:
    :param radius:
    :param types: 0 - ищем только банки, 1 ищем все
    :return:
    """
    spn = calculate_spn(radius)
    url = f"https://search-maps.yandex.ru/v1/"

    params = {
        "apikey": yandex_api_key,
        "text": query,
        "lang": "ru_RU",
        "ll": f"{lng},{lat}",
        "results": "50",
        "skip": f"{skip}"
    }

    headers = {
        "Accept": "application/json",
    }

    response = requests.request("GET", url, params=params)
    data = response.json()
    return data


if __name__ == '__main__':
    # Москва
    # lat = 55.7522200
    # lng = 37.6155600
    # Ставрополь
    # lat = 45.0428
    # lng = 41.9734
    coordinates = [(45.0428, 41.9734), (55.75222, 37.61556)]
    services = [
        "Открытие счета", "Получение кредита", "Обмен валюты",
        "Оформление ипотеки", "Кредиит для бизнеса", "Кредитная карта", "Дебетовая карта"
    ]
    load_type = ["Полная", "Средняя", "Малая"]
    week = {
        0: "Дни недели",
        1: "Выходные",
        2: "Каждый день",

        3: "Понедельник",
        4: "Вторник",
        5: "Среда",
        6: "Четверг",
        7: "Пятница",
        8: "Суббота",
        9: "Воскресенье",

    }
    day_keys = [
        'Weekdays',
        'Weekend',
        'Everyday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]

    for cord in coordinates:
        for i in range(100):
            data = map_search_yandex(cord[0], cord[1], "ВТБ", 4000000, skip=i * 50)
            data = data.get('features')
            if len(data) == 0:
                break
            for bank in data:
                if bank['properties']['CompanyMetaData']['Categories'][0]['class'] == 'banks':
                    coordinates = bank.get('geometry').get('coordinates')
                    company_metadata = bank.get('properties').get('CompanyMetaData')
                    category = company_metadata.get('Categories')[-1].get('class')
                    hours = company_metadata.get('Hours')
                    phones = company_metadata.get('Phones')
                    address = company_metadata.get('address')
                    name = company_metadata.get('name')
                    text_hours = hours['text']
                    bank_id = insert_bank_info(
                        bank_name=name,
                        work_hours=text_hours,
                        address=address,
                        services=", ".join(sample(services, randint(1, len(services)))),
                        latitude=coordinates[1],
                        longitude=coordinates[0],
                        load_type=choice(load_type),
                    )

                    for day in hours['Availabilities']:
                        is_working = []
                        for day_type in day_keys:
                            if day.get(day_type) is not None:
                                is_working.append(True)
                            else:
                                is_working.append(False)

                        working_time = "24ч"
                        if day.get('Intervals') is not None:
                            working_time = day.get('Intervals')[0]

                        for idx, status in enumerate(is_working):
                            if status:
                                if idx == 0:
                                    for j in range(3, 8):
                                        if working_time != "24ч":
                                            insert_availabilities(week[j], working_time['from'], working_time['to'],
                                                                  bank_id)
                                        else:
                                            insert_availabilities(week[j], "00:00", "00:00", bank_id)
                                    break
                                elif idx == 1:
                                    for j in range(8, 10):
                                        if working_time != "24ч":
                                            insert_availabilities(week[j], working_time['from'], working_time['to'],
                                                                  bank_id)
                                        else:
                                            insert_availabilities(week[j], "00:00", "00:00", bank_id)
                                    break
                                elif idx == 2:
                                    for j in range(3, 10):
                                        if working_time != "24ч":
                                            insert_availabilities(week[j], working_time['from'], working_time['to'],
                                                                  bank_id)
                                        else:
                                            insert_availabilities(week[j], "00:00", "00:00", bank_id)
                                    break
                                else:
                                    if working_time != "24ч":
                                        insert_availabilities(week[idx], working_time['from'], working_time['to'],
                                                              bank_id)
                                    else:
                                        insert_availabilities(week[idx], "00:00", "00:00", bank_id)
                if len(data) != 50:
                    break

    bank_data = select_all_bank_info()
    start_date = datetime.date(2023, 10, 1)
    end_date = datetime.date(2023, 10, 15)
    current_date = start_date
    while current_date <= end_date:
        for bank in bank_data:
            bank_id = bank['bank_id']
            schedule = bank['work_schedule']
            for i in range(len(schedule)):
                day_of_week = schedule[i][0]
                time_from = schedule[i][1].hour * 60 + schedule[i][1].minute
                time_to = schedule[i][2].hour * 60 + schedule[i][2].minute
                for time in range(time_from, time_to, 60):
                    insert_average_load(
                        current_date,
                        day_of_week,
                        datetime.time(time // 60, 0),
                        datetime.time((time + 60) // 60, 0),
                        load_by_time(time // 60),
                        bank_id
                    )
        current_date += datetime.timedelta(days=1)
    #
