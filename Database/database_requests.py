import math
import datetime
import random

from Database.settings import user, password, host, db_name
from sqlalchemy import (
    create_engine,
    delete,
    select,
    and_,
    asc,
    desc,
    func,
    update,
    insert,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import and_, or_, not_
from Database.tables import (
    banks_table,
    availabilities_table,
    history_table,
    average_load_table,
    atm_table,
    atm_availabilities_table,
)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from pprint import pprint

engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8mb4"
)
Session = sessionmaker(bind=engine)
session = Session()
connection = engine.connect()

model = RandomForestRegressor(n_estimators=100, random_state=0)


def predict_time(time):
    current_date = datetime.datetime.now() - datetime.timedelta(days=1)

    date_range = [current_date - datetime.timedelta(days=i) for i in range(len(time))]
    date_range.reverse()

    data_10 = pd.DataFrame({"Дата": date_range, "Посещаемость": time})

    X = np.arange(len(data_10)).reshape(-1, 1)
    y = data_10['Посещаемость']

    model.fit(X, y)
    next_day = len(data_10)

    predicted_value = model.predict([[next_day]])[0]
    return predicted_value


def haversine(lat1, lng1, lat2, lng2):
    lat1 = math.radians(lat1)
    lng1 = math.radians(lng1)
    lat2 = math.radians(lat2)
    lng2 = math.radians(lng2)
    earth_radius = 6371.0
    d_lng = lng2 - lng1
    d_lat = lat2 - lat1
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c
    return distance


def get_extended_info(bank_id):
    print(bank_id)
    s = select([
        banks_table.c.bank_name,
        banks_table.c.services,
        banks_table.c.work_hours,
        banks_table.c.address,
        banks_table.c.latitude,
        banks_table.c.longitude,
        banks_table.c.load_type
    ]).select_from(banks_table).where(banks_table.c.id == bank_id)

    bank_data = connection.execute(s)

    s = select([
        availabilities_table.c.day_of_week,
        availabilities_table.c.time_from,
        availabilities_table.c.time_to,
    ]).where(bank_id == availabilities_table.c.bank_id)

    availabilities_data = connection.execute(s)

    return [list(bank_data.fetchone()), list(availabilities_data.fetchall())]


def insert_bank_info(
        bank_name, work_hours, address, services, latitude,
        longitude, load_type, rko, network, office_type,
        sale_point_format, suo_availability, has_ramp
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
        has_ramp=has_ramp
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

    selected_banks = []

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
    for bank in selected_banks:
        status = "Закрыто"
        for day in bank[-1]:
            if day[0] == current_day_of_week:
                if day[1] <= req_time.time() <= day[2] or day[1] == day[2]:
                    status = "Открыто"
                break
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

    result_to_return = {"banks": data_to_return}

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


def insert_history(bank_id):
    history = history_table.insert().values(
        bank_id=bank_id,
        visit_time=datetime.datetime.now()
    )
    session.execute(history)
    session.commit()


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


def get_history():
    s = select([
        history_table.c.id,
        history_table.c.visit_time,
        history_table.c.bank_id,
    ]).select_from(history_table).order_by(history_table.c.visit_time.desc())

    result = connection.execute(s)

    return result.fetchall()


def delete_history(bank_id):
    history = history_table.delete().where(history_table.c.bank_id == bank_id)
    session.execute(history)
    session.commit()


def get_working_time(bank_id, weeks=1):
    current_date = datetime.datetime.now()
    last_date = current_date - datetime.timedelta(days=7 * weeks)
    current_date = current_date.date()
    last_date = last_date.date()
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
            average_load_table.c.time_from == datetime.time(10, 0),
            average_load_table.c.time_from == datetime.time(13, 0),
            average_load_table.c.time_from == datetime.time(16, 0),
        )
    ))
    time_data = connection.execute(s).fetchall()
    time_10 = []
    time_13 = []
    time_16 = []
    for elem in time_data:
        if elem[2] == datetime.time(10, 0):
            time_10.append(elem[4])
        elif elem[2] == datetime.time(13, 0):
            time_13.append(elem[4])
        elif elem[2] == datetime.time(16, 0):
            time_16.append(elem[4])
    return {
        "10": predict_time(time_10),
        "13": predict_time(time_13),
        "16": predict_time(time_16)
    }


if __name__ == '__main__':
    bank_info = get_banks_in_radius(45.0428, 41.9734, None, None, "1")
    pprint(bank_info)
