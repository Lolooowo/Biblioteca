from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import json

# --- Config ---
DB_NAME = "biblioteca.db"
LOCK_MINUTES = 3
MAX_INTENTOS = 3

app = Flask(__name__)
# Ajusta los orígenes según tu front (Live Server usa 127.0.0.1:5500 / localhost:5500)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://127.0.0.1:5500", "http://localhost:5500"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# --- Helpers DB ---
def conn():
    c = sqlite3.connect(DB_NAME, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as c:
        # Usuarios (almacenamos password en texto por simplicidad del proyecto)
        # Recomendado: usar hashes (werkzeug.security) en un proyecto real
        c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            tiempo INTEGER NOT NULL,
            categorias TEXT NOT NULL
            CHECK (json_valid(categorias))
        )
        """)
        # Intentos de login y bloqueo
        c.execute("""
        CREATE TABLE IF NOT EXISTS intentos_login (
            usuario   TEXT PRIMARY KEY,
            fallos    INTEGER NOT NULL DEFAULT 0,
            bloqueado_hasta TEXT
        )
        """.strip())

def get_intentos(usuario: str):
    with conn() as c:
        row = c.execute("SELECT fallos, bloqueado_hasta FROM intentos_login WHERE usuario = ?", (usuario,)).fetchone()
        if not row:
            return 0, None
        return row["fallos"], row["bloqueado_hasta"]

def set_intentos(usuario: str, fallos: int, bloqueado_hasta: str | None):
    with conn() as c:
        c.execute("""
        INSERT INTO intentos_login(usuario, fallos, bloqueado_hasta)
        VALUES(?,?,?)
        ON CONFLICT(usuario) DO UPDATE SET fallos=excluded.fallos, bloqueado_hasta=excluded.bloqueado_hasta
        """, (usuario, fallos, bloqueado_hasta))

# --- Rutas API ---
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    usuario = (data.get("usuario") or "").strip()
    password = (data.get("password") or data.get("contrasena") or "").strip()
    tiempo_libre = data.get("tiempo_libre")
    categorias = data.get("categorias")

    if not usuario or not password:
        return jsonify({"ok": False, "message": "Falta usuario o password"}), 400
    if not isinstance(tiempo_libre, int):
        return jsonify({"ok": False, "message": "Tiempo libre debe ser un entero"}), 400
    if not isinstance(categorias, list) or not all(isinstance(x, str) for x in categorias):
        return jsonify({"ok": False, "message": "categorias debe ser un array de strings"}), 400
    categorias_json = json.dumps(categorias, ensure_ascii=False)

    try:
        with conn() as c:
            c.execute(
                "INSERT INTO usuarios(usuario, password, tiempo,categorias) VALUES(?,?,?,?)",
                ( usuario,password,tiempo_libre,categorias_json)
            )
        # Limpia intentos previos si existían
        set_intentos(usuario, 0, None)
        return jsonify({"ok": True, "message": "Usuario registrado"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"ok": False, "message": "El usuario ya existe"}), 409

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    user = (data.get("usuario") or data.get("user") or "").strip()
    contrasena = data.get("contrasena") or data.get("password") or ""

    if not (user and contrasena):
        return jsonify({"ok": False, "message": "Credenciales incompletas"}), 400

    # Revisa bloqueos
    fallos, bloqueado_hasta = get_intentos(user)
    now = datetime.utcnow()
    if bloqueado_hasta:
        try:
            hasta = datetime.fromisoformat(bloqueado_hasta)
            if now < hasta:
                return jsonify({"ok": False, "locked": True, "attempts_left": 0, "message": "Cuenta bloqueada temporalmente"}), 423
        except Exception:
            pass 

    with conn() as c:
        row = c.execute("SELECT password FROM usuarios WHERE usuario = ?", (user,)).fetchone()
    if row and row["password"] == contrasena:
        # Login correcto: resetea intentos
        set_intentos(user, 0, None)
        return jsonify({"ok": True, "message": "Bienvenido"}), 200

    # Falla de login
    fallos = (fallos or 0) + 1
    if fallos >= MAX_INTENTOS:
        bloqueado = (now + timedelta(minutes=LOCK_MINUTES)).isoformat()
        set_intentos(user, fallos, bloqueado)
        return jsonify({"ok": False, "locked": True, "attempts_left": 0, "message": "Demasiados intentos. Cuenta bloqueada temporalmente"}), 401

    set_intentos(user, fallos, None)
    return jsonify({"ok": False, "locked": False, "attempts_left": MAX_INTENTOS - fallos, "message": "Usuario o contraseña incorrectos"}), 401

# --- Main ---
if __name__ == "__main__":
    init_db()
    import os
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "127.0.0.1")  # usa 0.0.0.0 si deseas otras máquinas
    print(f"🚀 API corriendo en http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)
