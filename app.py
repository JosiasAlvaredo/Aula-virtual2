from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"  # cámbiala por algo único

# Conexión a MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",   # pon tu password real
        database="aula_virtual"
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # viene del formulario de login
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        else:
            return "Correo o contraseña incorrectos"

    return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    nombre = request.form["nombre"]
    email = request.form["email"]
    password = request.form["password"]

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
                    (nombre, email, hashed))
    conn.commit()
    conn.close()
    return redirect(url_for("login"))

# Ruta protegida (index)
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

# Cerrar sesión
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
