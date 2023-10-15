import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))

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
    DECIMAL
)

from Database.settings import user, password, host, db_name

engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8mb4"
)
metadata = MetaData()

# Таблица "banks_table" для банков
banks_table = Table('banks_table', metadata,
                    Column('id', INTEGER(), primary_key=True,
                           autoincrement=True),  # Идентификатор
                    Column('bank_name', VARCHAR(70),  # Название банка (не может быть пустым)
                           nullable=False),
                    Column('work_hours', VARCHAR(60)),  # Рабочие часы
                    Column('address', VARCHAR(256)),  # Адрес
                    Column('rko', BOOLEAN()),  # Наличие РКО (Расчетно-кассовое обслуживание)
                    Column('network', VARCHAR(256)),  # Сеть
                    Column('office_type', VARCHAR(256)),  # Тип офиса
                    Column('sale_point_format', VARCHAR(256)),  # Формат точки продаж
                    Column('suo_availability', BOOLEAN()),  # Наличие СУО (Система управления обслуживанием)
                    Column('has_ramp', BOOLEAN()),  # Наличие пандуса
                    Column('services', VARCHAR(256)),  # Услуги
                    Column('latitude', DECIMAL(6, 4)),  # Широта
                    Column('longitude', DECIMAL(7, 4)),  # Долгота
                    Column('load_type', VARCHAR(15)),  # Тип нагрузки
                    Column('phone', VARCHAR(250)),  # Телефон
                    )

# Таблица "atm_table" для банкоматов
atm_table = Table('atm_table', metadata,
                  Column('id', INTEGER(), primary_key=True,
                         autoincrement=True),  # Идентификатор
                  Column('name', VARCHAR(70),
                         nullable=False),  # Название банкомата (не может быть пустым)
                  Column('work_hours', VARCHAR(60)),  # Рабочие часы
                  Column('address', VARCHAR(256)),  # Адрес
                  Column('has_ramp', BOOLEAN()),  # Наличие пандуса
                  Column('latitude', DECIMAL(6, 4)),  # Широта
                  Column('longitude', DECIMAL(7, 4)),  # Долгота
                  )

# Таблица "availabilities_table" для доступности банков
availabilities_table = Table('availabilities_table', metadata,
                             Column('id', INTEGER(), primary_key=True,
                                    autoincrement=True),  # Идентификатор
                             Column('day_of_week', VARCHAR(25)),  # День недели
                             Column('time_from', TIME()),  # Время начала работы
                             Column('time_to', TIME()),   # Время окончания работы
                             Column('bank_id', INTEGER(),
                                    ForeignKey('banks_table.id')),  # Идентификатор банка (внешний ключ)
                             )

# Таблица "atm_availabilities_table" для доступности банкоматов
atm_availabilities_table = Table('atm_availabilities_table', metadata,
                                 Column('id', INTEGER(), primary_key=True,
                                        autoincrement=True),  # Идентификатор
                                 Column('day_of_week', VARCHAR(25)),  # День недели
                                 Column('time_from', TIME()),  # Время начала работы
                                 Column('time_to', TIME()),  # Время окончания работы
                                 Column('atm_id', INTEGER(),
                                        ForeignKey('atm_table.id')),  # Идентификатор банкомата (внешний ключ)
                                 )


# Таблица "average_load_table" для средней загрузки
average_load_table = Table('average_load_table', metadata,
                           Column('id', INTEGER(), primary_key=True,
                                  autoincrement=True),  # Идентификатор
                           Column('date', DATE()),  # Дата
                           Column('day_of_week', VARCHAR(25)),  # День недели
                           Column('time_from', TIME()),   # Время начала
                           Column('time_to', TIME()),   # Время окончания
                           Column('average_load', INTEGER()),  # Средняя загрузка
                           Column('bank_id', INTEGER(),
                                  ForeignKey('banks_table.id')),   # Идентификатор банка (внешний ключ)
                           )

metadata.create_all(engine)
