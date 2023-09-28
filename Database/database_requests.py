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
