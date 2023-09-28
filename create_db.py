from mysql.connector import connect, Error
from Database.settings import host, user, password


if __name__ == '__main__':
    con = connect(
        host=host,
        user=user,
        password=password,
    )
    cur = con.cursor()
    create_db_query = "CREATE DATABASE IF NOT EXISTS banks_database"
    cur.execute(create_db_query)
    show_db_query = "SHOW DATABASES"
    cur.execute(show_db_query)
    data = cur.fetchall()
    for db in data:
        print(db)
    con.close()
