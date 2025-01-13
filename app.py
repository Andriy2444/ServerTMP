from flask import Flask
import mysql.connector
import os

app = Flask(__name__)

# Отримуємо змінні середовища
db_host = os.getenv('mysql-3a741e88-andriy241179-ec70.b.aivencloud.com')
db_port = os.getenv('16912')
db_name = os.getenv('user_data')
db_user = os.getenv('avnadmin')
db_password = os.getenv('AVNS_JC_0Jo0L4Fd3pL9kCPn')


# Підключення до бази даних MySQL
def get_db_connection():
    connection = mysql.connector.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    return connection


@app.route("/")
def home():
    try:
        # Підключення до бази
        connection = get_db_connection()
        cursor = connection.cursor()

        # Приклад запиту: отримуємо всі користувачів
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()

        # Формуємо відповідь на основі даних з бази
        users_list = "\n".join([f"Name: {user[1]}, Password: {user[2]}" for user in users])

        return f"Hello, Render!\nUsers in DB:\n{users_list}"

    except mysql.connector.Error as err:
        return f"Помилка підключення до бази даних: {err}"

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)