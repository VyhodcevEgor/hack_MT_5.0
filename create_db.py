from mysql.connector import connect, Error
from Database.settings import host, user, password


if __name__ == '__main__':
    # Устанавливаем соединение с базой данных
    con = connect(
        host=host,
        user=user,
        password=password,
    )
    cur = con.cursor()

    # Создаем запрос для создания базы данных "banks_database", если она не существует
    create_db_query = "CREATE DATABASE IF NOT EXISTS banks_database"
    cur.execute(create_db_query)

    # Запрос для получения списка всех баз данных
    show_db_query = "SHOW DATABASES"
    cur.execute(show_db_query)
    data = cur.fetchall()

    # Выводим список баз данных
    for db in data:
        print(db)

    # Закрываем соединение с базой данных
    con.close()

