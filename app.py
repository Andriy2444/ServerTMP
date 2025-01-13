from flask import Flask
import mysql.connector
import os

app = Flask(__name__)

# Отримуємо змінні середовища
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

# Перевірка на наявність всіх змінних середовища
if not all([db_host, db_port, db_name, db_user, db_password]):
    raise ValueError("Не всі змінні середовища для бази даних задані!")

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
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                # Приклад запиту: отримуємо всі користувачів
                cursor.execute("SELECT * FROM users;")
                users = cursor.fetchall()

                # Формуємо відповідь на основі даних з бази
                users_list = "\n".join([f"Name: {user[1]}, Password: {user[2]}" for user in users])

        return f"Hello, Render!\nUsers in DB:\n{users_list}"

    except mysql.connector.Error as err:
        return f"Помилка підключення до бази даних: {err}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
