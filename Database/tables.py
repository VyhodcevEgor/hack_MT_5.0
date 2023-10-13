from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    VARCHAR,
    INTEGER,
    Column,
    TIME,
    BOOLEAN,
    DATE,
    ForeignKey,
    DECIMAL,
    DATETIME
)
from Database.settings import user, password, host, db_name

engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8mb4"
)
metadata = MetaData()

banks_table = Table('banks_table', metadata,
                    Column('id', INTEGER(), primary_key=True,
                           autoincrement=True),
                    Column('bank_name', VARCHAR(70),
                           nullable=False),  # was unique=True
                    Column('work_hours', VARCHAR(60)),
                    Column('address', VARCHAR(256)),
                    Column('rko', BOOLEAN()),
                    Column('network', VARCHAR(256)),
                    Column('office_type', VARCHAR(256)),
                    Column('sale_point_format', VARCHAR(256)),
                    Column('suo_availability', BOOLEAN()),
                    Column('has_ramp', BOOLEAN()),
                    Column('services', VARCHAR(256)),
                    Column('latitude', DECIMAL(6, 4)),
                    Column('longitude', DECIMAL(7, 4)),
                    Column('load_type', VARCHAR(15)),
                    Column('phone', VARCHAR(20)),
                    )
availabilities_table = Table('availabilities_table', metadata,
                             Column('id', INTEGER(), primary_key=True,
                                    autoincrement=True),
                             Column('day_of_week', VARCHAR(25)),
                             Column('time_from', TIME()),
                             Column('time_to', TIME()),
                             Column('bank_id', INTEGER(),
                                    ForeignKey('banks_table.id')),
                             )

history_table = Table('history_table', metadata,
                      Column('id', INTEGER(), primary_key=True,
                             autoincrement=True),
                      Column('visit_time', DATETIME()),
                      Column('bank_id', INTEGER(),
                             ForeignKey('banks_table.id')),
                      )

average_load_table = Table('average_load_table', metadata,
                           Column('id', INTEGER(), primary_key=True,
                                  autoincrement=True),
                           Column('date', DATE()),
                           Column('day_of_week', VARCHAR(25)),
                           Column('time_from', TIME()),
                           Column('time_to', TIME()),
                           Column('average_load', INTEGER()),
                           Column('bank_id', INTEGER(),
                                  ForeignKey('banks_table.id')),
                           )

metadata.create_all(engine)
