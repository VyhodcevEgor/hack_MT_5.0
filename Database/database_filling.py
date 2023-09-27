from Database.settings import user, password, host, db_name, yandex_api_key
from Database.database_requests import insert_bank_info, insert_availabilities
from random import sample, randint, choice
from pprint import pprint
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
import requests

engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8mb4"
)


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
        #"spn": f"{spn[0]},{spn[1]}",
        #"rspn": "1",
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
    lat = 45.0428
    lng = 41.9734
    services = [
        "Открытие счета", "Получение кредита", "Обмен валюты",
        "Оформление ипотеки", "Кредиит для бизнеса", "Кредитная карта", "Дебетовая карта"
    ]
    load_type = ["Полная", "Средняя", "Малая"]
    for i in range(100):
        data = map_search_yandex(lat, lng, "ВТБ", 4000000, skip=i * 50)
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
                    day_keys = ['Weekdays', 'Weekend', 'Everyday', 'Monday',
                                'Tuesday', 'Wednesday', 'Thursday',
                                'Friday', 'Saturday', 'Sunday'
                                ]
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
                                        insert_availabilities(week[j], working_time['from'], working_time['to'], bank_id)
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
                                    insert_availabilities(week[idx], working_time['from'], working_time['to'], bank_id)
                                else:
                                    insert_availabilities(week[idx], "00:00", "00:00", bank_id)
                        # print(idx, status)
            if len(data) != 50:
                break
