import math
import datetime
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
from Database.tables import banks_table, availabilities_table

engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8mb4"
)
Session = sessionmaker(bind=engine)
session = Session()
connection = engine.connect()


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

    result = connection.execute(s)

    return result.fetchone()


def insert_bank_info(
        bank_name, work_hours, address, services, latitude,
        longitude, load_type
):
    bank = banks_table.insert().values(
        bank_name=bank_name,
        work_hours=work_hours,
        address=address,
        services=services,
        latitude=latitude,
        longitude=longitude,
        load_type=load_type
    )
    result_proxy = session.execute(bank)
    session.commit()
    return result_proxy.inserted_primary_key[0]


def insert_availabilities(day_of_week, time_from, time_to, bank_id):
    availability = availabilities_table.insert().values(
        day_of_week=day_of_week,
        time_from=time_from,
        time_to=time_to,
        bank_id=bank_id,
    )
    session.execute(availability)
    session.commit()


def get_banks_in_radius(lat, lng, service, loading_type, distance):
    if not distance:
        distance = 1

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

            for day in work_hours:
                if day[0] == current_day_of_week:
                    selected_banks.append(list(bank) + list(day))

    if loading_type is not None:
        selected_banks = [bank for bank in selected_banks if loading_type in bank]
    if service is not None:
        selected_banks = [bank for bank in selected_banks if service in bank[5]]
    data_to_return = []
    for bank in selected_banks:
        temp = {
            "bank_id": bank[0],
            "name": bank[1],
            "load_type": bank[2],
            "lat": str(float(bank[3])),
            "lng": str(float(bank[4])),
            "services": bank[5],
            "day": bank[6],
            "from": bank[7].strftime("%H:%M"),
            "to": bank[8].strftime("%H:%M"),
        }
        data_to_return.append(temp)
    return data_to_return


#if __name__ == '__main__':
#    get_banks_in_radius(55.7522200, 37.6155600, "Оформление ипотеки", "Средняя", 4)
