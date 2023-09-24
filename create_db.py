from mysql.connector import connect, Error
from Database.settings import host, user, password


if __name__ == '__main__':
    try:
        with connect(
            host=host,
            user=user,
            password=password,
        ) as connection:
            print(connection)
            create_db_query = "CREATE DATABASE banks_database"
            with connection.cursor() as cursor:
                cursor.execute(create_db_query)
    except Error as e:
        print(e)

    with connect(
            host="localhost",
            user='evil_inc',
            password='qwop010702',
    ) as connection:
        show_db_query = "SHOW DATABASES"
        with connection.cursor() as cursor:
            cursor.execute(show_db_query)
            for db in cursor:
                print(db)
