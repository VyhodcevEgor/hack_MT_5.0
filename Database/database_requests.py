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
)
from Database.tables import banks_table


engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8mb4"
)
connection = engine.connect()


def get_extended_info(bank_id):
    print(bank_id)
    s = select([
        banks_table.c.bank_name,
        banks_table.c.services,
        banks_table.c.work_hours,
        banks_table.c.latitude,
        banks_table.c.longitude,
        banks_table.c.load_type
    ]).select_from(banks_table).where(banks_table.c.id == bank_id)

    result = connection.execute(s)

    return result.fetchone()
