from flask import Flask, request, render_template
import mysql.connector
import os
import bcrypt
import logging

app = Flask(__name__)

# Налаштування логування
logging.basicConfig(level=logging.INFO)

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

if not all([db_host, db_port, db_name, db_user, db_password]):
    raise ValueError("Не всі змінні середовища для бази даних задані!")

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        return connection
    except mysql.connector.Error as err:
        logging.error(f"Не вдалося підключитися до бази даних: {err}")
        return None

def reset_user_password(username, new_password):
    # Генерація нового bcrypt хешу для пароля
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    connection = get_db_connection()
    if connection is None:
        return False

    try:
        with connection.cursor() as cursor:
            # Оновлення пароля в базі даних
            cursor.execute("UPDATE users SET password = %s WHERE name = %s",
                           (hashed_password.decode('utf-8'), username))
            connection.commit()
            logging.info(f"Пароль для користувача {username} оновлено.")
            return True
    except mysql.connector.Error as err:
        logging.error(f"Помилка при оновленні пароля: {err}")
        return False
    finally:
        if connection:
            connection.close()

def verify_user(username, password, newpassword):
    try:
        connection = get_db_connection()
        if connection is None:
            return False

        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE name = %s", (username,))
            user = cursor.fetchone()

            if user:
                stored_password_hash = user[0]
                # Перевірка на кілька можливих префіксів bcrypt
                if stored_password_hash.startswith(("$2b$", "$2a$")):
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                        return True
                else:
                    logging.warning(f"Пароль користувача {username} має некоректний формат хешу. Перезбереження пароля...")
                    # Оновити пароль з новим хешем
                    reset_user_password(username, newpassword)
            else:
                logging.warning(f"Користувач {username} не знайдений.")
    except mysql.connector.Error as err:
        logging.error(f"Помилка бази даних: {err}")
    finally:
        if connection:
            connection.close()

    return False

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if verify_user(username, password, "password123"):
            return render_template("index.html", message="Login successful!")
        else:
            return render_template("index.html", message="Invalid username or password.")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
