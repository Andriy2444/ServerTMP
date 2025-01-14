from flask import Flask, request, render_template
import mysql.connector
import os
import bcrypt

app = Flask(__name__)

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

if not all([db_host, db_port, db_name, db_user, db_password]):
    raise ValueError("Не всі змінні середовища для бази даних задані!")

def get_db_connection():
    connection = mysql.connector.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    return connection

def verify_user(username, password):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                if user and bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):
                    return True
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    return False

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if verify_user(username, password):
            return "Login successful!"
        else:
            return "Invalid username or password.", 401

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)