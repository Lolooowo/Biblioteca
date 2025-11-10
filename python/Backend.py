from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import json
import os
import random
import ast
DB_NAME = "biblioteca.db"
LOCK_MINUTOS = 3
MAX_INTENTOS = 3
PAG_POR_HORA = 30
usuario_permanente = ""
app = Flask(__name__)
app.secret_key = "elizabethrosebloodflame"
ALLOWED_ORIGINS = {
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",
    "http://localhost:5500",
    "http://localhost:5501",
}

CORS(app,
     resources={r"/api/*": {"origins": list(ALLOWED_ORIGINS)}},
     supports_credentials=True)

@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS and request.path.startswith("/api/"):
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
        resp.headers["Access-Control-Allow-Credentials"] = "true"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return resp
def conn():
    c = sqlite3.connect(DB_NAME, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON;")
    return c
def leyendo():
    with conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS leyendo (
                user     TEXT    NOT NULL,
                id_libro TEXT NOT NULL,
                plan     INTEGER NOT NULL,
                PRIMARY KEY (user, id_libro),
                FOREIGN KEY (user)     REFERENCES usuarios(usuario)   ON DELETE CASCADE,
                FOREIGN KEY (id_libro) REFERENCES libros(id_libro)    ON DELETE CASCADE
            );
        """)
def por_leer():
    with conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS por_leer (
                user     TEXT    NOT NULL,
                id_libro TEXT NOT NULL,
                PRIMARY KEY (user, id_libro),
                FOREIGN KEY (user)     REFERENCES usuarios(usuario)   ON DELETE CASCADE,
                FOREIGN KEY (id_libro) REFERENCES libros(id_libro)    ON DELETE CASCADE
            );
        """)
def leido():
    with conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS leido (
                user     TEXT    NOT NULL,
                id_libro TEXT NOT NULL,
                PRIMARY KEY (user, id_libro),
                FOREIGN KEY (user)     REFERENCES usuarios(usuario)   ON DELETE CASCADE,
                FOREIGN KEY (id_libro) REFERENCES libros(id_libro)    ON DELETE CASCADE
            );
        """)
class Usuario:
    @staticmethod
    def init_tablas_usuario():
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
    def _get_categorias_usuario(usuario: str):
        with conn() as c:
            fila = c.execute(
                "SELECT categorias FROM usuarios WHERE usuario = ?",
                (usuario,)
            ).fetchone()
        if not fila:
            return []
        try:
            return json.loads(fila["categorias"])
        except Exception:
            return []
    @staticmethod
    def _pick_random_categoria(cats):
        if not cats:
            return None
        return random.choice(cats)
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
            cat_random = Usuario._pick_random_categoria(categorias_list)
            session["usuario"] = usuario
            return {
                "ok": True,
                "message": "Usuario registrado",
                "categoria_sugerida": cat_random,
                "usuario": usuario
            }, 201
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
                    return {
                        "ok": False,
                        "locked": True,
                        "attempts_left": 0,
                        "message": "Cuenta bloqueada temporalmente"
                    }, 423
            except Exception:
                pass
        with conn() as c:
            row = c.execute(
                "SELECT password, categorias FROM usuarios WHERE usuario = ?",
                (user,)
            ).fetchone()
        if row and row["password"] == password:
            Usuario._set_intentos(user, 0, None)
            try:
                cats = json.loads(row["categorias"])
            except Exception:
                cats = []
            cat_random = Usuario._pick_random_categoria(cats)
            session["usuario"] = user
            usuario_permanente = user
            return {
                "ok": True,
                "message": "Bienvenido",
                "categoria_sugerida": cat_random,
                "usuario": user
            }, 200
        fails = (fails or 0) + 1
        if fails >= MAX_INTENTOS:
            bloqueado_hasta = (now + timedelta(minutes=LOCK_MINUTES)).isoformat()
            Usuario._set_intentos(user, fails, bloqueado_hasta)
            return {
                "ok": False,
                "locked": True,
                "attempts_left": 0,
                "message": "Demasiados intentos. Cuenta bloqueada temporalmente"
            }, 401
        Usuario._set_intentos(user, fails, None)
        return {
            "ok": False,
            "locked": False,
            "attempts_left": MAX_INTENTOS - fails,
            "message": "Usuario o contraseña incorrectos"
        }, 401
class Libro:
    @staticmethod
    def init_tablas_libro():
        with conn() as c:
            c.execute("""
            CREATE TABLE IF NOT EXISTS libros (
                   id_libro TEXT PRIMARY KEY,
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
    def agregar(c,payload):
        id_libro = payload.get("id_libro") or payload.get("id")
        titulo = (payload.get("titulo") or "").strip()
        autores = (payload.get("autores") or "")
        categoria = (payload.get("categoria") or "").strip()
        portada = (payload.get("portada") or "").strip()
        descripcion = (payload.get("descripcion") or "").strip()
        paginas = payload.get("paginas")
        editorial = (payload.get("editorial") or "").strip()
        idioma = (payload.get("idioma") or "").strip()
        enlace = (payload.get("enlace") or "").strip()
        autores = json.dumps(autores, ensure_ascii=False) if isinstance(autores, list) else autores
        if id_libro is None:
            return {"ok": False, "message": "id_libro debe ser un entero"}, 400
        campos_txt = [titulo, autores, categoria, portada, descripcion, editorial, idioma, enlace]
        # if any(not x for x in campos_txt):
        #     return {"ok": False, "message": "Faltan campos de texto obligatorios"}, 400
        if not isinstance(paginas, int) or paginas <= 0:
            return {"ok": False, "message": "paginas debe ser entero > 0"}, 400
        try:
            with c:
                c.execute(
                    """INSERT INTO libros
                       (id_libro, titulo, autores, categoria, portada, descripcion, paginas, editorial, idioma, enlace)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (id_libro, titulo, autores, categoria, portada, descripcion, paginas, editorial, idioma, enlace)
                )
            return {"ok": True, "message": "Libro agregado", "id_libro": id_libro}, 201
        except sqlite3.IntegrityError:
            return {"ok": False, "message": "El libro ya existe (id duplicado)"}, 409
def parse_autores(raw):
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if x is not None]
    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return []
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if x is not None]
        except Exception:
            pass
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple)):
                return [str(x).strip() for x in parsed if x is not None]
        except Exception:
            pass
        for sep in (",", ";", "|"):
            if sep in s:
                parts = [p.strip() for p in s.split(sep) if p.strip()]
                if parts:
                    return parts
        return [s]
    return [str(raw)]
@app.route("/api/por-leer", methods=["POST"])
def api_agregar_por_leer():
    user = session.get("usuario")
    if not user:
        return jsonify({"ok": False, "message": "No hay sesión"}), 401
    data = request.get_json() or {}
    id_libro = data.get("id_libro")
    book_payload = data.get("book") or data
    if id_libro is None:
        return jsonify({"ok": False, "message": "Falta id_libro en el JSON"}), 400
    conn_obj = conn()
    try:
        with conn_obj as c:
            if not c.execute("SELECT 1 FROM libros WHERE id_libro = ?", (id_libro,)).fetchone():
                keys = set(book_payload.keys()) if isinstance(book_payload, dict) else set()
                if keys <= {"id_libro", "id"}:
                    return jsonify({"ok": False, "message": "El libro no existe. Envía los campos del libro para crearlo o crea el libro primero."}), 400
                body, code = Libro.agregar(c, book_payload)
                if code == 409 or code == 201:
                    pass
                else:
                    if code != 201:
                        return jsonify({"ok": False, "message": body["message"], "detail": body}), 400
            try:
                c.execute("INSERT INTO por_leer (user, id_libro) VALUES (?, ?)", (user, id_libro))
            except sqlite3.IntegrityError as e:
                return jsonify({"ok": False, "message": "No se pudo agregar a por_leer", "detail": str(e)}), 400
        return jsonify({"ok": True, "message": "Agregado a por leer", "id_libro": id_libro}), 201
    finally:
        conn_obj.close()
@app.route("/api/leido", methods=["POST"])
def api_agregar_leido():
    user = session.get("usuario")
    if not user:
        return jsonify({"ok": False, "message": "No hay sesión activa"}), 401
    data = request.get_json() or {}
    id_libro = data.get("id_libro")
    book_payload = data.get("book") or data
    if id_libro is None:
        return jsonify({"ok": False, "message": "Falta id_libro en el JSON"}), 400
    conn_obj = conn()
    try:
        with conn_obj as c:
            libro_existe = c.execute(
                "SELECT 1 FROM libros WHERE id_libro = ?", (id_libro,)
            ).fetchone()
            if not libro_existe:
                keys = set(book_payload.keys()) if isinstance(book_payload, dict) else set()
                if keys <= {"id_libro", "id"}:
                    return jsonify({
                        "ok": False,
                        "message": "El libro no existe y no se enviaron datos suficientes para crearlo."
                    }), 400
                body, code = Libro.agregar(c, book_payload)
                if code != 201:
                    return jsonify({
                        "ok": False,
                        "message": "No se pudo crear el libro",
                        "detail": body
                    }), 400
            try:
                c.execute("INSERT INTO leido (user, id_libro) VALUES (?, ?)", (user, id_libro))
            except sqlite3.IntegrityError as e:
                return jsonify({
                    "ok": False,
                    "message": "El libro ya está en la lista de leídos o ocurrió un error",
                    "detail": str(e)
                }), 400
        return jsonify({
            "ok": True,
            "message": "Libro agregado correctamente a 'leído'",
            "id_libro": id_libro
        }), 201
    finally:
        conn_obj.close()
@app.route("/api/leyendo", methods=["POST"])
def api_agregar_leyendo():
    user = session.get("usuario")
    if not user:
        return jsonify({"ok": False, "message": "No hay sesión activa"}), 401
    data = request.get_json() or {}
    id_libro = data.get("id_libro")
    horas_dia = data.get("horas_dia")
    book_payload = data.get("book") or data
    if id_libro is None:
        return jsonify({"ok": False, "message": "Falta id_libro en el JSON"}), 400
    if horas_dia is None:
        return jsonify({"ok": False, "message": "Falta horas_dia en el JSON"}), 400
    try:
        horas_dia = float(horas_dia)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "horas_dia inválido"}), 400
    if horas_dia <= 0:
        return jsonify({"ok": False, "message": "horas_dia debe ser mayor que 0"}), 400
    conn_obj = conn()
    try:
        with conn_obj as c:
            if not c.execute("SELECT 1 FROM libros WHERE id_libro = ?", (id_libro,)).fetchone():
                keys = set(book_payload.keys()) if isinstance(book_payload, dict) else set()
                if keys <= {"id_libro", "id"}:
                    return jsonify({
                        "ok": False,
                        "message": "El libro no existe y no se enviaron datos suficientes para crearlo."
                    }), 400
                body, code = Libro.agregar(c, book_payload)
                if code != 201:
                    return jsonify({
                        "ok": False,
                        "message": "No se pudo crear el libro",
                        "detail": body
                    }), 400
            fila = c.execute("SELECT tiempo FROM usuarios WHERE usuario = ?", (user,)).fetchone()
            if not fila:
                return jsonify({"ok": False, "message": "Usuario no encontrado"}), 404
            try:
                tiempo_libre = float(fila["tiempo"])
            except Exception:
                tiempo_libre = 0.0
            if tiempo_libre <= 0:
                return jsonify({"ok": False, "message": "No tienes horas libres para agregar nuevos planes de lectura"}), 400
            if horas_dia > tiempo_libre:
                return jsonify({"ok": False, "message": "No tienes suficiente tiempo libre para este plan"}), 400
            if c.execute("SELECT 1 FROM leyendo WHERE user = ? AND id_libro = ?", (user, id_libro)).fetchone():
                return jsonify({"ok": False, "message": "Este libro ya está en tu lista de lectura"}), 409
            try:
                c.execute("INSERT INTO leyendo (user, id_libro, plan) VALUES (?, ?, ?)", (user, id_libro, horas_dia))
            except sqlite3.IntegrityError as e:
                return jsonify({
                    "ok": False,
                    "message": "No se pudo agregar a 'leyendo' (integrity error)",
                    "detail": str(e)
                }), 400
            nuevo_tiempo = tiempo_libre - horas_dia
            c.execute("UPDATE usuarios SET tiempo = ? WHERE usuario = ?", (nuevo_tiempo, user))
        return jsonify({
            "ok": True,
            "message": "Libro agregado al plan de lectura",
            "id_libro": id_libro,
            "horas_dia": horas_dia,
            "tiempo_libre_restante": nuevo_tiempo
        }), 201
    finally:
        conn_obj.close()
@app.route("/api/leidos", methods=["GET"])
def api_listar_leidos():
    user = session.get("usuario")
    if not user:
        return jsonify({"ok": False, "message": "No hay sesión activa"}), 401
    with conn() as c:
        filas = c.execute("""
            SELECT l.id_libro, l.titulo, l.autores, l.categoria, l.portada,
                   l.descripcion, l.paginas, l.editorial, l.idioma, l.enlace
            FROM leido li
            JOIN libros l ON l.id_libro = li.id_libro
            WHERE li.user = ?
            ORDER BY l.titulo
        """, (user,)).fetchall()
    libros = []
    for f in filas:
        d = dict(f)
        d["autores"] = parse_autores(d.get("autores"))
        libros.append(d)
    return jsonify({"ok": True, "count": len(libros), "libros": libros}), 200
@app.route("/api/leyendos", methods=["GET"])
def api_listar_leyendo():
    user = session.get("usuario")
    if not user:
        return jsonify({"ok": False, "message": "No hay sesión activa"}), 401
    with conn() as c:
        filas = c.execute("""
            SELECT l.id_libro, l.titulo, l.autores, l.categoria, l.portada,
                   l.descripcion, l.paginas, l.editorial, l.idioma, l.enlace,
                   ly.plan
              FROM leyendo ly
              JOIN libros l ON l.id_libro = ly.id_libro
             WHERE ly.user = ?
             ORDER BY l.titulo
        """, (user,)).fetchall()
    libros = []
    for f in filas:
        d = dict(f)
        if "plan" in d:
            try:
                d["plan"] = float(d["plan"])
            except Exception:
                pass
            d["autores"] = parse_autores(d.get("autores"))
        libros.append(d)
    return jsonify({"ok": True, "count": len(libros), "libros": libros}), 200
@app.route("/api/por-leers", methods=["GET"])
def api_listar_por_leer():
    user = session.get("usuario")
    if not user:
        return jsonify({"ok": False, "message": "No hay sesión activa"}), 401
    with conn() as c:
        filas = c.execute("""
            SELECT l.id_libro, l.titulo, l.autores, l.categoria, l.portada,
                   l.descripcion, l.paginas, l.editorial, l.idioma, l.enlace
              FROM por_leer pl
              JOIN libros l ON l.id_libro = pl.id_libro
             WHERE pl.user = ?
             ORDER BY l.titulo
        """, (user,)).fetchall()
        libros = []
    for f in filas:
        d = dict(f)
        d["autores"] = parse_autores(d.get("autores"))
        libros.append(d)
    return jsonify({"ok": True, "count": len(libros), "libros": libros}), 200
@app.route("/api/mover_a_leidos", methods=["POST", "OPTIONS"])
def api_mover_a_leidos():
    if request.method == "OPTIONS":
        return ("", 204)

    user = session.get("usuario")
    if not user:
        return jsonify({"ok": False, "message": "No hay sesión activa"}), 401

    data = request.get_json() or {}
    id_libro = data.get("id_libro")
    if not id_libro:
        return jsonify({"ok": False, "message": "Falta el id_libro"}), 400

    # Ojo: corrige nombres de tablas/columnas para que existan de verdad
    with conn() as c:
        fila_leyendo = c.execute("""
            SELECT plan FROM leyendo
             WHERE user = ? AND id_libro = ?
        """, (user, id_libro)).fetchone()
        if not fila_leyendo:
            return jsonify({"ok": False, "message": "El libro no está en 'leyendo'"}), 404

        plan_horas = float(fila_leyendo["plan"])

        # Normaliza nombres de columnas: en tu código usas 'tiempo' y también 'horas_libres'
        # Elige una columna real; aquí asumo 'tiempo' que sí creaste en usuarios.
        c.execute("""
            UPDATE usuarios
               SET tiempo = tiempo + ?
             WHERE usuario = ?
        """, (plan_horas, user))

        # Normaliza nombre de tabla: tienes 'leido' y también usas 'leidos' aquí.
        # Usa 'leido' que sí creaste arriba.
        c.execute("""
            INSERT INTO leido (user, id_libro)
            VALUES (?, ?)
        """, (user, id_libro))

        c.execute("""
            DELETE FROM leyendo
             WHERE user = ? AND id_libro = ?
        """, (user, id_libro))

    return jsonify({"ok": True, "message": "Libro movido a 'leído' correctamente"}), 200
@app.route("/api/leidos/delete", methods=["POST"])
def api_delete_leido():
    user = session.get("usuario")
    if not user:
        return jsonify({"ok": False, "message": "No hay sesión activa"}), 401
    data = request.get_json() or {}
    id_libro = data.get("id_libro")
    if id_libro is None:
        return jsonify({"ok": False, "message": "Falta id_libro en el JSON"}), 400
    id_libro = str(id_libro).strip()
    try:
        with conn() as c:
            row = c.execute(
                "SELECT * FROM leidos WHERE id_libro = ? AND usuario = ?",
                (id_libro, user)
            ).fetchone()
            if not row:
                return jsonify({
                    "ok": False,
                    "message": "El libro no se encuentra en la tabla de leídos"
                }), 404
            c.execute(
                "DELETE FROM leidos WHERE id_libro = ? AND usuario = ?",
                (id_libro, user)
            )
            c.commit()
        return jsonify({
            "ok": True,
            "message": "Libro eliminado correctamente de la tabla leídos",
            "id_libro": id_libro
        }), 200
    except Exception as e:
        return jsonify({
            "ok": False,
            "message": f"Error al eliminar el libro: {e}"
        }), 500
@app.route("/api/mover_por_leer_a_leyendo", methods=["POST"])
def api_mover_por_leer_a_leyendo():
    user = session.get("usuario")
    if not user:
        return jsonify({"ok": False, "message": "No hay sesión activa"}), 401
    data = request.get_json() or {}
    id_libro = data.get("id_libro")
    horas_dia = data.get("horas_dia")
    if id_libro is None:
        return jsonify({"ok": False, "message": "Falta id_libro en el JSON"}), 400
    if horas_dia is None:
        return jsonify({"ok": False, "message": "Falta horas_dia en el JSON"}), 400
    conn_obj = conn()
    try:
        with conn_obj as c:
            c.execute("PRAGMA foreign_keys = ON;")
            if not c.execute("SELECT 1 FROM libros WHERE id_libro = ?", (id_libro,)).fetchone():
                return jsonify({"ok": False, "message": "El libro no existe en la base de datos"}), 404
            if not c.execute("SELECT 1 FROM por_leer WHERE user = ? AND id_libro = ?", (user, id_libro)).fetchone():
                return jsonify({"ok": False, "message": "El libro no está en tu lista 'por leer'"}), 404
            fila_user = c.execute("SELECT tiempo FROM usuarios WHERE usuario = ?", (user,)).fetchone()
            columna_tiempo = "tiempo"
            if not fila_user:
                fila_user = c.execute("SELECT horas_libres FROM usuarios WHERE usuario = ?", (user,)).fetchone()
                columna_tiempo = "horas_libres"
            if not fila_user:
                return jsonify({"ok": False, "message": "Usuario no encontrado"}), 404
            try:
                tiempo_actual = float(fila_user[0])
            except Exception:
                tiempo_actual = 0.0
            if tiempo_actual <= 0:
                return jsonify({"ok": False, "message": "No tienes horas libres disponibles"}), 400
            if horas_dia > tiempo_actual:
                return jsonify({"ok": False, "message": "No tienes suficiente tiempo libre para este plan"}), 400
            if c.execute("SELECT 1 FROM leyendo WHERE user = ? AND id_libro = ?", (user, id_libro)).fetchone():
                return jsonify({"ok": False, "message": "El libro ya está en tu lista 'leyendo'"}), 409
            try:
                c.execute("INSERT INTO leyendo (user, id_libro, plan) VALUES (?, ?, ?)", (user, id_libro, horas_dia))
            except sqlite3.IntegrityError as e:
                return jsonify({"ok": False, "message": "No se pudo agregar a 'leyendo'", "detail": str(e)}), 400
            nuevo_tiempo = tiempo_actual - horas_dia
            c.execute(f"UPDATE usuarios SET {columna_tiempo} = ? WHERE usuario = ?", (nuevo_tiempo, user))
            c.execute("DELETE FROM por_leer WHERE user = ? AND id_libro = ?", (user, id_libro))
            return jsonify({
                "ok": True,
                "message": "Libro movido a 'leyendo' correctamente",
                "id_libro": id_libro,
                "horas_dia": horas_dia,
                "tiempo_libre_restante": nuevo_tiempo
            }), 201
    finally:
        conn_obj.close()
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
@app.route("/api/me", methods=["GET"])
def api_me():
    user = session.get("usuario")
    if not user:
        return jsonify({"ok": False, "message": "No hay sesión"}), 401
    cats = Usuario._get_categorias_usuario(user)
    return jsonify({"ok": True, "usuario": user, "cat": cats}), 200
@app.route("/api/libros", methods=["POST"])
def api_libros_create():
    data = request.get_json() or {}
    body, code = Libro.agregar(data)
    return jsonify(body), code
if __name__ == "__main__":
    Usuario.init_tablas_usuario()
    Libro.init_tablas_libro()
    leyendo()       
    por_leer()
    leido()
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "127.0.0.1")
    print(f"API en http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)