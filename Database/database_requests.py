import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))

import datetime
import math
import random
from pprint import pprint

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import (
    create_engine,
    select,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import and_, or_

from Database.settings import user, password, host, db_name
from Database.tables import (
    banks_table,
    availabilities_table,
    average_load_table,
    atm_table,
    atm_availabilities_table,
)

engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8mb4"
)
Session = sessionmaker(bind=engine)
session = Session()
connection = engine.connect()

model = RandomForestRegressor(n_estimators=100, random_state=0)


def get_times_to_predict(bank_id, weeks, time_for_prediction):
    current_date = datetime.datetime.now()  # Текущая дата и время
    last_date = current_date - datetime.timedelta(days=7 * weeks)  # Дата, отстоящая на weeks недель
    current_date = current_date.date()  # Текущая дата
    last_date = last_date.date()

    # Запрос к базе данных для получения временных данных для прогнозирования
    s = select([
        average_load_table.c.date,
        average_load_table.c.day_of_week,
        average_load_table.c.time_from,
        average_load_table.c.time_to,
        average_load_table.c.average_load,
    ]).where(and_(
        average_load_table.c.bank_id == bank_id,
        average_load_table.c.date >= last_date,
        average_load_table.c.date < current_date,
        or_(
            average_load_table.c.time_from == datetime.time(time_for_prediction, 0),
        )
    ))
    query_data = connection.execute(s).fetchall()

    # Возвращаем список средних загрузок для каждого элемента в query_data
    return [int(elem[4]) for elem in query_data]


def predict_time(time):
    current_date = datetime.datetime.now() - datetime.timedelta(days=1)

    date_range = [current_date - datetime.timedelta(days=i) for i in range(len(time))]
    date_range.reverse()

    # Создаем DataFrame с данными о дате и посещаемости
    data_10 = pd.DataFrame({"Дата": date_range, "Посещаемость": time})

    x = np.arange(len(data_10)).reshape(-1, 1)
    y = data_10['Посещаемость']

    model.fit(x, y)  # Обучаем модель на данных
    next_day = len(data_10)

    predicted_value = model.predict([[next_day]])[0]  # Прогнозируем значение для следующего дня
    return predicted_value


def haversine(lat1, lng1, lat2, lng2):
    lat1 = math.radians(lat1)  # Преобразуем широту 1 в радианы
    lng1 = math.radians(lng1)  # Преобразуем долготу 1 в радианы
    lat2 = math.radians(lat2)  # Преобразуем широту 2 в радианы
    lng2 = math.radians(lng2)  # Преобразуем долготу 2 в радианы
    earth_radius = 6371.0  # Радиус Земли в километрах
    d_lng = lng2 - lng1  # Разница долгот
    d_lat = lat2 - lat1  # Разница широт
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng / 2) ** 2  # Формула haversine
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))  # Вычисление угла между точками
    distance = earth_radius * c  # Вычисление расстояния между точками
    return distance


def get_atm_extended_info(atm_id):
    s = select([
        atm_table.c.name,
        atm_table.c.work_hours,
        atm_table.c.address,
        atm_table.c.has_ramp,
        atm_table.c.latitude,
        atm_table.c.longitude,
    ]).select_from(atm_table).where(atm_table.c.id == atm_id)
    atm_data = connection.execute(s)
    s = select([
        atm_availabilities_table.c.day_of_week,
        atm_availabilities_table.c.time_from,
        atm_availabilities_table.c.time_to,
    ]).where(atm_id == atm_availabilities_table.c.bank_id)
    availabilities_data = connection.execute(s)

    atm_data = atm_data.fetchone()
    availabilities_data = availabilities_data.fetchall()

    data_to_return = {
        "bank_name": atm_data[0],
        "address": atm_data[2],
        "has_ramp": atm_data[3],
        'ext_work_hours': []
    }
    for day in availabilities_data:
        data_to_return['ext_work_hours'].append(
            {
                'days': day[0],
                'hours': f'{day[1].strftime("%H:%M")}-{day[2].strftime("%H:%M")}',
                "from": f'{day[1].strftime("%H:%M")}',
                "to": f'{day[2].strftime("%H:%M")}',
            }
        )
    return data_to_return


def get_extended_info(bank_id):
    s = select([
        banks_table.c.bank_name,
        banks_table.c.services,
        banks_table.c.work_hours,
        banks_table.c.address,
        banks_table.c.latitude,
        banks_table.c.longitude,
        banks_table.c.load_type,
        banks_table.c.phone,
    ]).select_from(banks_table).where(banks_table.c.id == bank_id)

    bank_data = connection.execute(s)

    s = select([
        availabilities_table.c.day_of_week,
        availabilities_table.c.time_from,
        availabilities_table.c.time_to,
    ]).where(bank_id == availabilities_table.c.bank_id)

    availabilities_data = connection.execute(s)
    bank_data = bank_data.fetchone()
    availabilities_data = availabilities_data.fetchall()
    current_hour = int(datetime.datetime.now().strftime("%H"))
    data_to_return = {
        "bank_name": bank_data[0],
        "services": bank_data[1],
        "address": bank_data[3],
        'latitude': float(bank_data[4]),
        'longitude': float(bank_data[5]),
        # 'load_type': bank_data[6],
        'phone': bank_data[7],
        "reviews_count": random.randint(20, 500),
        "reviews_score": random.uniform(1, 5),
        'ext_work_hours': [],
        'predicted_time': get_working_time(bank_id),
        "currentLoad": predict_time(get_times_to_predict(bank_data[0], 1, current_hour))
    }
    for day in availabilities_data:
        data_to_return['ext_work_hours'].append(
            {
                'days': day[0],
                'hours': f'{day[1].strftime("%H:%M")}-{day[2].strftime("%H:%M")}',
                "from": f'{day[1].strftime("%H:%M")}',
                "to": f'{day[2].strftime("%H:%M")}',
            }
        )
    return data_to_return


def insert_bank_info(
        bank_name, work_hours, address, services, latitude,
        longitude, load_type, rko, network, office_type,
        sale_point_format, suo_availability, has_ramp, phone
):
    bank = banks_table.insert().values(
        bank_name=bank_name,
        work_hours=work_hours,
        address=address,
        services=services,
        latitude=latitude,
        longitude=longitude,
        load_type=load_type,
        rko=rko,
        network=network,
        office_type=office_type,
        sale_point_format=sale_point_format,
        suo_availability=suo_availability,
        has_ramp=has_ramp,
        phone=phone
    )
    result_proxy = session.execute(bank)
    session.commit()
    return result_proxy.inserted_primary_key[0]


def insert_atm_info(
        name, work_hours, address, latitude,
        longitude, has_ramp
):
    atm = atm_table.insert().values(
        name=name,
        work_hours=work_hours,
        address=address,
        latitude=latitude,
        longitude=longitude,
        has_ramp=has_ramp,
    )
    result_proxy = session.execute(atm)
    session.commit()
    return result_proxy.inserted_primary_key[0]


def select_all_bank_info():
    data_to_return = []
    s = select([
        banks_table.c.id
    ]).select_from(banks_table)
    bank_data = connection.execute(s).fetchall()
    for data in bank_data:
        s = select([
            availabilities_table.c.day_of_week,
            availabilities_table.c.time_from,
            availabilities_table.c.time_to,
        ]).where(data[0] == availabilities_table.c.bank_id)
        availabilities_data = connection.execute(s).fetchall()
        data_to_return.append({
            "bank_id": data[0],
            "work_schedule": availabilities_data
        }
        )
    return data_to_return


def insert_availabilities(day_of_week, time_from, time_to, bank_id, entity_type):
    if entity_type == "bank":
        availability = availabilities_table.insert().values(
            day_of_week=day_of_week,
            time_from=time_from,
            time_to=time_to,
            bank_id=bank_id,
        )
        session.execute(availability)
        session.commit()
    else:
        availability = atm_availabilities_table.insert().values(
            day_of_week=day_of_week,
            time_from=time_from,
            time_to=time_to,
            atm_id=bank_id,
        )
        session.execute(availability)
        session.commit()


def get_banks_in_radius(lat, lng, service, loading_type, distance):
    # Если расстояние не указано, устанавливаем значение по умолчанию равным 1
    if not distance:
        distance = 1
    else:
        distance = int(distance)

    days_of_week_russian = [
        "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"
    ]

    current_datetime = datetime.datetime.now()
    current_day_of_week = current_datetime.weekday()
    current_day_of_week = days_of_week_russian[current_day_of_week]

    # Запрос для выборки данных о банках
    s = select([
        banks_table.c.id,
        banks_table.c.bank_name,
        banks_table.c.load_type,
        banks_table.c.latitude,
        banks_table.c.longitude,
        banks_table.c.services,
        banks_table.c.address,
        banks_table.c.rko,
        banks_table.c.network,
        banks_table.c.office_type,
        banks_table.c.sale_point_format,
        banks_table.c.suo_availability,
        banks_table.c.has_ramp
    ])

    result = connection.execute(s)
    banks_data = result.fetchall()

    # Список для хранения выбранных банкоматов
    selected_banks = []

    # Проверка расстояния между координатами и выборка банков в заданном радиусе
    for bank in banks_data:

        dist = haversine(lat, lng, float(bank[3]), float(bank[4]))

        if dist <= distance:
            s = select([
                availabilities_table.c.day_of_week,
                availabilities_table.c.time_from,
                availabilities_table.c.time_to,
            ]).where(bank[0] == availabilities_table.c.bank_id)
            result = connection.execute(s)
            work_hours = result.fetchall()
            temp = list(bank)
            temp.append([])
            for day in work_hours:
                temp[-1].append(list(day))
            selected_banks.append(temp)

    if loading_type is not None:
        selected_banks = [bank for bank in selected_banks if loading_type in bank]
    if service is not None:
        selected_banks = [bank for bank in selected_banks if service in bank[5]]
    data_to_return = []
    req_time = datetime.datetime.now()

    # Обработка данных о банках
    for bank in selected_banks:
        status = "Закрыто"
        for day in bank[-1]:
            if day[0] == current_day_of_week:
                if day[1] <= req_time.time() <= day[2] or day[1] == day[2]:
                    status = "Открыто"
                break
        current_hour = int(datetime.datetime.now().strftime("%H"))
        temp = {
            "bankId": bank[0],
            "salesPointName": bank[1],
            "address": bank[6],
            "salePointCode": bank[0],
            "status": status,
            "openHours": [],
            "rko": bank[7],
            "network": None,
            "openHoursIndividual": [],
            "officeType": bank[9],
            "salePointFormat": bank[10],
            "suoAvailability": bank[11],
            "hasRamp": bank[12],
            "latitude": str(float(bank[3])),
            "longitude": str(float(bank[4])),
            "metroStation": None,
            "distance": None,
            "kep": bool(random.randint(0, 1)),
            "myBranch": False,
            "loadType": get_working_time(bank[0]),
            "services": bank[5],
            "currentLoad": predict_time(get_times_to_predict(bank[0], 1, current_hour))
        }
        for day in bank[-1]:
            work_day = {
                'days': day[0],
                'hours': f'{day[1].strftime("%H:%M")}-{day[2].strftime("%H:%M")}',
                "from": f'{day[1].strftime("%H:%M")}',
                "to": f'{day[2].strftime("%H:%M")}',
            }
            temp['openHours'].append(work_day)
            temp['openHoursIndividual'].append(work_day)
        data_to_return.append(temp)

    # Формирование результирующего словаря с данными о банках и банкоматах
    result_to_return = {"banks": data_to_return}

    # Запрос для выборки данных о банкоматах
    s = select([
        atm_table.c.id,
        atm_table.c.name,
        atm_table.c.latitude,
        atm_table.c.longitude,
        atm_table.c.address,
        atm_table.c.has_ramp
    ])

    result = connection.execute(s)
    atm_data = result.fetchall()

    selected_atms = []

    # Проверка расстояния между координатами и выборка банкоматов в заданном радиусе
    for atm in atm_data:

        dist = haversine(lat, lng, float(atm[2]), float(atm[3]))

        if dist <= distance:
            s = select([
                atm_availabilities_table.c.day_of_week,
                atm_availabilities_table.c.time_from,
                atm_availabilities_table.c.time_to,
            ]).where(atm[0] == atm_availabilities_table.c.atm_id)
            result = connection.execute(s)
            work_hours = result.fetchall()
            temp = list(atm)
            temp.append([])
            for day in work_hours:
                temp[-1].append(list(day))
            selected_atms.append(temp)

    data_to_return = []

    # Обработка данных о банкоматах
    for atm in selected_atms:
        status = "Закрыто"
        for day in atm[-1]:
            if day[0] == current_day_of_week:
                if day[1] <= req_time.time() <= day[2] or day[1] == day[2]:
                    status = "Открыто"
                break
        temp = {
            "atmId": atm[0],
            "salesPointName": f"Банкомат {atm[1]}",
            "address": atm[4],
            "status": status,
            "openHours": [],
            "openHoursIndividual": [],
            "hasRamp": atm[5],
        }
        for day in atm[-1]:
            work_day = {
                'days': day[0],
                'hours': f'{day[1].strftime("%H:%M")}-{day[2].strftime("%H:%M")}',
                "from": f'{day[1].strftime("%H:%M")}',
                "to": f'{day[2].strftime("%H:%M")}',
            }
            temp['openHours'].append(work_day)
            temp['openHoursIndividual'].append(work_day)
        data_to_return.append(temp)
    result_to_return['atms'] = data_to_return
    return result_to_return


def insert_average_load(date, day_of_week, time_from, time_to, average_load, bank_id):
    load = average_load_table.insert().values(
        date=date,
        day_of_week=day_of_week,
        time_from=time_from,
        time_to=time_to,
        average_load=average_load,
        bank_id=bank_id,
    )
    session.execute(load)
    session.commit()


def get_working_time(bank_id, weeks=1):
    return {
        "10": predict_time(get_times_to_predict(bank_id, weeks, 10)),
        "13": predict_time(get_times_to_predict(bank_id, weeks, 13)),
        "16": predict_time(get_times_to_predict(bank_id, weeks, 15))
    }


if __name__ == '__main__':
    bank_info = get_banks_in_radius(55.7522200, 37.6155600, None, None, "100")
    pprint(bank_info)
