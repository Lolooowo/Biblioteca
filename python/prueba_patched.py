from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import json
import os

DB_NAME = "biblioteca.db"
LOCK_MINUTES = 3
MAX_INTENTOS = 3

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://127.0.0.1:5500", "http://127.0.0.1:5501", "http://localhost:5500", "http://localhost:5501"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def conn():
    c = sqlite3.connect(DB_NAME, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON;")
    return c

class Usuario:
    @staticmethod
    def init_tablas():
        with conn() as c:
            c.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                tiempo   INTEGER NOT NULL,
                categorias TEXT NOT NULL
                CHECK (json_valid(categorias))
            )
            """)
            c.execute("""
            CREATE TABLE IF NOT EXISTS intentos_login (
              user TEXT PRIMARY KEY,
              fails INTEGER NOT NULL DEFAULT 0,
              locked_until TEXT
            )
            """)

    @staticmethod
    def _get_intentos(user):
        with conn() as c:
            row = c.execute(
                "SELECT fails, locked_until FROM intentos_login WHERE user=?",
                (user,)
            ).fetchone()
            if not row:
                return 0, None
            return row["fails"], row["locked_until"]

    @staticmethod
    def _set_intentos(user, fails, locked_until):
        with conn() as c:
            c.execute("""
                INSERT INTO intentos_login(user, fails, locked_until)
                VALUES(?,?,?)
                ON CONFLICT(user) DO UPDATE SET fails=excluded.fails, locked_until=excluded.locked_until
            """, (user, fails, locked_until))

    @staticmethod
    def registrar(usuario, password, tiempo_libre, categorias_list):
        if not usuario or not password:
            return {"ok": False, "message": "Falta usuario o password"}, 400
        if not isinstance(tiempo_libre, int):
            return {"ok": False, "message": "Tiempo libre debe ser un entero"}, 400
        if not isinstance(categorias_list, list) or not all(isinstance(x, str) for x in categorias_list):
            return {"ok": False, "message": "categorias debe ser un array de strings"}, 400
        categorias_json = json.dumps(categorias_list, ensure_ascii=False)
        try:
            with conn() as c:
                c.execute(
                    "INSERT INTO usuarios(usuario, password, tiempo, categorias) VALUES(?,?,?,?)",
                    (usuario, password, tiempo_libre, categorias_json)
                )
            Usuario._set_intentos(usuario, 0, None)
            return {"ok": True, "message": "Usuario registrado"}, 201
        except sqlite3.IntegrityError:
            return {"ok": False, "message": "El usuario ya existe"}, 409

    @staticmethod
    def login(user, password):
        if not user or not password:
            return {"ok": False, "message": "Credenciales incompletas"}, 400
        fails, locked_until = Usuario._get_intentos(user)
        now = datetime.utcnow()
        if locked_until:
            try:
                locked_dt = datetime.fromisoformat(locked_until)
                if now < locked_dt:
                    return {"ok": False, "locked": True, "attempts_left": 0, "message": "Cuenta bloqueada temporalmente"}, 423
            except Exception:
                pass
        with conn() as c:
            row = c.execute("SELECT password FROM usuarios WHERE usuario = ?", (user,)).fetchone()
        if row and row["password"] == password:
            Usuario._set_intentos(user, 0, None)
            return {"ok": True, "message": "Bienvenido"}, 200
        fails = (fails or 0) + 1
        if fails >= MAX_INTENTOS:
            bloqueado_hasta = (now + timedelta(minutes=LOCK_MINUTES)).isoformat()
            Usuario._set_intentos(user, fails, bloqueado_hasta)
            return {"ok": False, "locked": True, "attempts_left": 0, "message": "Demasiados intentos. Cuenta bloqueada temporalmente"}, 401
        Usuario._set_intentos(user, fails, None)
        return {"ok": False, "locked": False, "attempts_left": MAX_INTENTOS - fails, "message": "Usuario o contraseña incorrectos"}, 401

class Libro:
    def __init__(self, id, titulo, autores, categoria, portada, descripcion, paginas, editorial, idioma, enlace):
        self.id = id
        self.titulo = titulo
        self.autores = autores
        self.categoria = categoria
        self.portada = portada
        self.descripcion = descripcion
        self.paginas = paginas
        self.editorial = editorial
        self.idioma = idioma
        self.enlace = enlace

    @staticmethod
    def init_tablas():
        with conn() as c:
            c.execute("""
            CREATE TABLE IF NOT EXISTS libros (
                   id_libro INTEGER PRIMARY KEY,
                   titulo TEXT NOT NULL,
                   autores TEXT NOT NULL,
                   categoria TEXT NOT NULL,
                   portada TEXT NOT NULL,
                   descripcion TEXT NOT NULL,
                   paginas INTEGER NOT NULL,
                   editorial TEXT NOT NULL,
                   idioma TEXT NOT NULL,
                   enlace TEXT NOT NULL
            )
            """)

    @staticmethod
    def agregar(payload):
        id_libro = payload.get("id_libro") or payload.get("id")
        titulo = (payload.get("titulo") or "").strip()
        autores = (payload.get("autores") or "").strip()
        categoria = (payload.get("categoria") or "").strip()
        portada = (payload.get("portada") or "").strip()
        descripcion = (payload.get("descripcion") or "").strip()
        paginas = payload.get("paginas")
        editorial = (payload.get("editorial") or "").strip()
        idioma = (payload.get("idioma") or "").strip()
        enlace = (payload.get("enlace") or "").strip()

        if id_libro is None or not isinstance(id_libro, int):
            return {"ok": False, "message": "id_libro debe ser un entero"}, 400
        campos_txt = [titulo, autores, categoria, portada, descripcion, editorial, idioma, enlace]
        if any(not x for x in campos_txt):
            return {"ok": False, "message": "Faltan campos de texto obligatorios"}, 400
        if not isinstance(paginas, int) or paginas <= 0:
            return {"ok": False, "message": "paginas debe ser entero > 0"}, 400

        try:
            with conn() as c:
                c.execute(
                    """INSERT INTO libros
                       (id_libro, titulo, autores, categoria, portada, descripcion, paginas, editorial, idioma, enlace)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (id_libro, titulo, autores, categoria, portada, descripcion, paginas, editorial, idioma, enlace)
                )
            return {"ok": True, "message": "Libro agregado", "id_libro": id_libro}, 201
        except sqlite3.IntegrityError:
            return {"ok": False, "message": "El libro ya existe (id duplicado)"}, 409

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    usuario = (data.get("usuario") or "").strip()
    password = (data.get("password") or data.get("contrasena") or "").strip()
    tiempo_libre = data.get("tiempo_libre")
    categorias_list = data.get("categorias")
    body, code = Usuario.registrar(usuario, password, tiempo_libre, categorias_list)
    return jsonify(body), code

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    user = (data.get("usuario") or data.get("user") or "").strip()
    contrasena = data.get("contrasena") or data.get("password") or ""
    body, code = Usuario.login(user, contrasena)
    return jsonify(body), code

@app.route("/api/libros", methods=["POST"])
def api_libros_create():
    data = request.get_json() or {}
    body, code = Libro.agregar(data)
    return jsonify(body), code
if __name__ == "__main__":
    Usuario.init_tablas()
    Libro.init_tablas()
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "127.0.0.1")
    print(f"API en http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)