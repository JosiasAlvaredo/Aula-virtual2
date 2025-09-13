from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "Renault12345"
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="aula_virtual"
    )

class Usuario:
    def __init__(self, id_usuario, nombre, apellido, posicion, email, contrasena, foto_perfil):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.posicion = posicion
        self.email = email
        self.contrasena = contrasena
        self.foto_perfil = foto_perfil

class Clase:
    def __init__(self, id_clase, nombre_clase, codigo_ingreso, banner, descripcion):
        self.id_clase = id_clase
        self.nombre_clase = nombre_clase
        self.codigo_ingreso = codigo_ingreso
        self.banner = banner
        self.descripcion = descripcion

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        if user and password == user["contrasena"]:
            session["user_id"] = user["id_usuario"]
            session["nombre"] = user["nombre"]
            session["posicion"] = user["posicion"]
            return redirect(url_for("index"))
        else:
            return "Correo o contraseña incorrectos"
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, apellido, email, contrasena) VALUES (%s, %s, %s, %s)",
                        (nombre, apellido, email, password))
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clases")
    clases = cursor.fetchall()
    conn.close()
    return render_template("index.html", clases=clases)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/clases")
def clases():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clases")
    clases = [Clase(c["id_clase"], c["nombre_clase"], c["codigo_ingreso"], c["banner"], c["descripcion"]) for c in cursor.fetchall()]
    conn.close()
    return render_template("clases.html", clases=clases)

@app.route("/clases/crear", methods=["POST"])
def crear_clase():
    if "user_id" not in session:
        return redirect(url_for("login"))
    nombre_clase = request.form["nombre_clase"]
    codigo_ingreso = request.form["codigo_ingreso"]
    banner = request.form["banner"]
    descripcion = request.form["descripcion"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clases (nombre_clase, codigo_ingreso, banner, descripcion) VALUES (%s, %s, %s, %s)",
                   (nombre_clase, codigo_ingreso, banner, descripcion))
    conn.commit()
    nueva_clase_id = cursor.lastrowid
    conn.close()
    return redirect(url_for("classroom", id_clase=nueva_clase_id))

@app.route("/clases/editar/<int:id_clase>", methods=["POST"])
def editar_clase(id_clase):
    if "user_id" not in session:
        return redirect(url_for("login"))
    nombre_clase = request.form["nombre_clase"]
    codigo_ingreso = request.form["codigo_ingreso"]
    banner = request.form["banner"]
    descripcion = request.form["descripcion"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE clases SET nombre_clase=%s, codigo_ingreso=%s, banner=%s, descripcion=%s WHERE id_clase=%s",
                   (nombre_clase, codigo_ingreso, banner, descripcion, id_clase))
    conn.commit()
    conn.close()
    return redirect(url_for("clases"))

@app.route("/clases/eliminar/<int:id_clase>")
def eliminar_clase(id_clase):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clases WHERE id_clase=%s", (id_clase,))
    conn.commit()
    conn.close()
    return redirect(url_for("clases"))

@app.route("/clase/<int:id_clase>", methods=["GET"])
def classroom(id_clase):
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clases WHERE id_clase = %s", (id_clase,))
    clase = cursor.fetchone()
    cursor.execute("""
        SELECT p.*, u.nombre as nombre_creador 
        FROM publicaciones p 
        JOIN usuarios u ON p.id_creador = u.id_usuario 
        WHERE p.id_clase = %s ORDER BY p.fecha_publicacion DESC
    """, (id_clase,))
    publicaciones = cursor.fetchall()
    for pub in publicaciones:
        cursor.execute("""
            SELECT mp.*, u.nombre as nombre_emisor 
            FROM mensajes_privados mp 
            JOIN usuarios u ON mp.id_emisor = u.id_usuario 
            WHERE mp.id_publicacion = %s
            ORDER BY mp.fecha_envio ASC
        """, (pub["id_publicacion"],))
        pub["comentarios"] = cursor.fetchall()
        if pub["entregable"]:
            cursor.execute("""
                SELECT e.*, u.nombre as nombre_alumno 
                FROM entregas e 
                JOIN usuarios u ON e.id_alumno = u.id_usuario 
                WHERE e.id_tarea = %s
            """, (pub["id_publicacion"],))
            pub["entregas"] = cursor.fetchall()
            for entrega in pub["entregas"]:
                cursor.execute("""
                    SELECT d.*, u.nombre as nombre_profesor 
                    FROM devoluciones d 
                    JOIN usuarios u ON d.id_profesor = u.id_usuario 
                    WHERE d.id_entrega = %s
                """, (entrega["id_entrega"],))
                entrega["devolucion"] = cursor.fetchone()
    conn.close()
    return render_template("classroom.html", clase=clase, publicaciones=publicaciones)

@app.route("/clase/<int:id_clase>/publicar", methods=["POST"])
def publicar(id_clase):
    if "user_id" not in session:
        return redirect(url_for("login"))
    mensaje = request.form["mensaje"]
    multimedia = None
    if "multimedia" in request.files:
        file = request.files["multimedia"]
        if file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            multimedia = "/" + filepath
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO publicaciones (id_clase, id_creador, mensaje, multimedia, entregable, bloquear_entrega) 
        VALUES (%s, %s, %s, %s, 0, 0)
    """, (id_clase, session["user_id"], mensaje, multimedia))
    conn.commit()
    conn.close()
    return redirect(url_for("classroom", id_clase=id_clase))

@app.route("/clase/<int:id_clase>/tarea", methods=["POST"])
def crear_tarea(id_clase):
    if "user_id" not in session:
        return redirect(url_for("login"))
    mensaje = request.form["mensaje"]
    fecha_entrega = request.form["fecha_entrega"]
    multimedia = None
    if "multimedia" in request.files:
        file = request.files["multimedia"]
        if file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            multimedia = "/" + filepath
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO publicaciones (id_clase, id_creador, mensaje, multimedia, entregable, fecha_entrega, bloquear_entrega) 
        VALUES (%s, %s, %s, %s, 1, %s, 0)
    """, (id_clase, session["user_id"], mensaje, multimedia, fecha_entrega))
    conn.commit()
    conn.close()
    return redirect(url_for("classroom", id_clase=id_clase))

@app.route("/publicacion/<int:id_publicacion>/comentar", methods=["POST"])
def comentar(id_publicacion):
    if "user_id" not in session:
        return redirect(url_for("login"))
    comentario = request.form["comentario"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mensajes_privados (id_publicacion, id_emisor, id_receptor, mensaje) 
        VALUES (%s, %s, NULL, %s)
    """, (id_publicacion, session["user_id"], comentario))
    cursor.execute("SELECT id_clase FROM publicaciones WHERE id_publicacion = %s", (id_publicacion,))
    id_clase = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return redirect(url_for("classroom", id_clase=id_clase))

@app.route("/tarea/<int:id_publicacion>/entregar", methods=["POST"])
def entregar_tarea(id_publicacion):
    if "user_id" not in session:
        return redirect(url_for("login"))
    multimedia = None
    if "multimedia" in request.files:
        file = request.files["multimedia"]
        if file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            multimedia = "/" + filepath
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO entregas (id_tarea, id_alumno, multimedia)
        VALUES (%s, %s, %s)
    """, (id_publicacion, session["user_id"], multimedia))
    cursor.execute("SELECT id_clase FROM publicaciones WHERE id_publicacion = %s", (id_publicacion,))
    id_clase = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return redirect(url_for("classroom", id_clase=id_clase))

@app.route("/entrega/<int:id_entrega>/calificar", methods=["POST"])
def calificar_entrega(id_entrega):
    if "user_id" not in session:
        return redirect(url_for("login"))
    calificacion = request.form["calificacion"]
    aclaraciones = request.form["aclaraciones"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO devoluciones (id_entrega, id_profesor, calificacion, aclaraciones)
        VALUES (%s, %s, %s, %s)
    """, (id_entrega, session["user_id"], calificacion, aclaraciones))
    cursor.execute("SELECT id_tarea FROM entregas WHERE id_entrega = %s", (id_entrega,))
    id_publicacion = cursor.fetchone()[0]
    cursor.execute("SELECT id_clase FROM publicaciones WHERE id_publicacion = %s", (id_publicacion,))
    id_clase = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return redirect(url_for("classroom", id_clase=id_clase))

if __name__ == "__main__":
    app.run(debug=True)