from flask import Flask, request, render_template
import mysql.connector
import os
import bcrypt
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

if not all([db_host, db_port, db_name, db_user, db_password]):
    raise ValueError("Not all database environment variables are set!")

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
        logging.error(f"Failed to connect to database: {err}")
        return None

# def reset_user_password(username, new_password):
#     # Генерація нового bcrypt хешу для пароля
#     hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
#
#     connection = get_db_connection()
#     if connection is None:
#         return False
#
#     try:
#         with connection.cursor() as cursor:
#             # Оновлення пароля в базі даних
#             cursor.execute("UPDATE users SET password = %s WHERE name = %s",
#                            (hashed_password.decode('utf-8'), username))
#             connection.commit()
#             logging.info(f"Пароль для користувача {username} оновлено.")
#             return True
#     except mysql.connector.Error as err:
#         logging.error(f"Помилка при оновленні пароля: {err}")
#         return False
#     finally:
#         if connection:
#             connection.close()

def verify_user(username, password):
    try:
        connection = get_db_connection()
        if connection is None:
            return False

        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE name = %s", (username,))
            user = cursor.fetchone()

            if user:
                stored_password_hash = user[0]
                if stored_password_hash.startswith(("$2b$", "$2a$")):
                    if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                        return True
                else:
                    logging.warning(f"Username: {username} has an incorrect hash format.")
            else:
                logging.warning(f"Username: {username} not found!.")
    except mysql.connector.Error as err:
        logging.error(f"Error dbo: {err}")
    finally:
        if connection:
            connection.close()

    return False

def register_user(username, password):
    connection = get_db_connection()
    if connection is None:
        return False, "Database connection failed."

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE name = %s", (username,))
            user = cursor.fetchone()

            if user:
                return False, "Username already exists."


            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            cursor.execute(
                "INSERT INTO users (name, password) VALUES (%s, %s)",
                (username, hashed_password.decode('utf-8'))
            )
            connection.commit()
            logging.info(f"User {username} successfully registered.")
            return True, "User registered successfully."

    except mysql.connector.Error as err:
        logging.error(f"Error during user registration: {err}")
        return False, "Database error occurred."

    finally:
        if connection:
            connection.close()

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template("register.html", message="Passwords do not match.")

        success, message = register_user(username, password)
        return render_template("register.html", message=message)

    return render_template("register.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if verify_user(username, password):
            return redirect(url_for("menu"))
        else:
            return render_template("index.html", message="Invalid username or password.")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
