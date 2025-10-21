import sqlite3
DB_NAME = "biblioteca.db"
def conn():
    c = sqlite3.connect(DB_NAME)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON;")
    return c
def leyendo():
    with conn() as c:
        c.execute("""
             CREATE TABLE IF NOT EXISTS leyendo (
                user     TEXT    NOT NULL,
                id_libro INTEGER NOT NULL,
                plan INTEGER NOT NULL,
                PRIMARY KEY (user, id_libro),
                FOREIGN KEY (user)     REFERENCES usuarios(user)     ON DELETE CASCADE,
                FOREIGN KEY (id_libro) REFERENCES libros(id_libro)   ON DELETE CASCADE
            );
        """)
def agregar_leyendo(user: str, id_libro: int,plan: int) -> bool:
    with conn() as c:
        if not c.execute("SELECT 1 FROM usuarios WHERE user=?", (user,)).fetchone():
            print("El usuario no existe."); return False
        if not c.execute("SELECT 1 FROM libros WHERE id_libro=?", (id_libro,)).fetchone():
            print("El libro no existe."); return False
        cur = c.execute(
            "INSERT OR IGNORE INTO leyendo (user, id_libro,plan) VALUES (?, ?,?)",
            (user, id_libro,plan)
        )
        inserted = (cur.rowcount == 1)
    print("Libro marcado por leer." if inserted else "Ya estaba marcado como por leer.")
    return inserted
def listar_leyendo(user: str):
    with conn() as c:
        filas = c.execute("""
            SELECT ll.id_libro, l.titulo
              FROM leyendo ll
              JOIN libros l ON l.id_libro = ll.id_libro
             WHERE ll.user = ?
             ORDER BY l.titulo
        """, (user,)).fetchall()
    if not filas:
        print(f"El usuario '{user}' no tiene libros en leyendo.")
        return
    print(f"\n--- LIBROS Leyendo por {user} ---")
    for f in filas:
        print(f"- ({f['id_libro']}) {f['titulo']}")
def por_leer():
    with conn() as c:
        c.execute("""
             CREATE TABLE IF NOT EXISTS por_leer (
                user     TEXT    NOT NULL,
                id_libro INTEGER NOT NULL,
                PRIMARY KEY (user, id_libro),
                FOREIGN KEY (user)     REFERENCES usuarios(user)     ON DELETE CASCADE,
                FOREIGN KEY (id_libro) REFERENCES libros(id_libro)   ON DELETE CASCADE
            );
        """)
def agregar_por_leer(user: str, id_libro: int) -> bool:
    with conn() as c:
        if not c.execute("SELECT 1 FROM usuarios WHERE user=?", (user,)).fetchone():
            print("El usuario no existe."); return False
        if not c.execute("SELECT 1 FROM libros WHERE id_libro=?", (id_libro,)).fetchone():
            print("El libro no existe."); return False
        cur = c.execute(
            "INSERT OR IGNORE INTO por_leer (user, id_libro) VALUES (?, ?)",
            (user, id_libro)
        )
        inserted = (cur.rowcount == 1)
    print("Libro marcado por leer." if inserted else "Ya estaba marcado como por leer.")
    return inserted
def listar_por_leer(user: str):
    with conn() as c:
        filas = c.execute("""
            SELECT ll.id_libro, l.titulo
              FROM por_leer ll
              JOIN libros l ON l.id_libro = ll.id_libro
             WHERE ll.user = ?
             ORDER BY l.titulo
        """, (user,)).fetchall()
    if not filas:
        print(f"El usuario '{user}' no tiene libros por leer.")
        return
    print(f"\n--- LIBROS POR LEER por {user} ---")
    for f in filas:
        print(f"- ({f['id_libro']}) {f['titulo']}")
def lidos():
    with conn() as c:
        c.execute("""
             CREATE TABLE IF NOT EXISTS leidos (
                user     TEXT    NOT NULL,
                id_libro INTEGER NOT NULL,
                PRIMARY KEY (user, id_libro),
                FOREIGN KEY (user)     REFERENCES usuarios(user)     ON DELETE CASCADE,
                FOREIGN KEY (id_libro) REFERENCES libros(id_libro)   ON DELETE CASCADE
            );
        """)
def agregar_leido(user: str, id_libro: int) -> bool:
    with conn() as c:
        if not c.execute("SELECT 1 FROM usuarios WHERE user=?", (user,)).fetchone():
            print("El usuario no existe."); return False
        if not c.execute("SELECT 1 FROM libros WHERE id_libro=?", (id_libro,)).fetchone():
            print("El libro no existe."); return False
        cur = c.execute(
            "INSERT OR IGNORE INTO leidos (user, id_libro) VALUES (?, ?)",
            (user, id_libro)
        )
        inserted = (cur.rowcount == 1)
    print("Libro marcado como leído." if inserted else "Ya estaba marcado como leído.")
    return inserted
def listar_leidos(user: str):
    with conn() as c:
        filas = c.execute("""
            SELECT ll.id_libro, l.titulo
              FROM leidos ll
              JOIN libros l ON l.id_libro = ll.id_libro
             WHERE ll.user = ?
             ORDER BY l.titulo
        """, (user,)).fetchall()
    if not filas:
        print(f"El usuario '{user}' no tiene libros leídos.")
        return
    print(f"\n--- LIBROS LEÍDOS por {user} ---")
    for f in filas:
        print(f"- ({f['id_libro']}) {f['titulo']}")
class Libro:
    def __init__(self, id, titulo,autores,categoria,portada,descripcion,paginas,editorial,idioma,enlace):
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
    def _conn():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        conn.execute("""
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
               );
           """)
        conn.commit()
        return conn
    def guardar(self):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO libros (id_libro, titulo, autores,categoria,portada,descripcion,paginas,editorial,idioma,"
                "enlace) VALUES (?, ?, ?,?,?,?,?,?,?,?)",
                (self.id, self.titulo, self.autores, self.categoria, self.portada, self.descripcion,self.paginas,
                 self.editorial, self.idioma, self.enlace)
            )
    @staticmethod
    def listar():
        with Libro._conn() as conn:
            cur = conn.execute("SELECT * FROM libros")
            filas = cur.fetchall()
            if not filas:
                print("No hay libros registrados.")
                return
            print("\n--- LISTADO DE LIBROS ---")
            for f in filas:
                print(
                    f"ID: {f['id_libro']} | Titulo: {f['titulo']} | Autor: {f['autores']} | Categoria: {f['categoria']}"
                    f" | Portada: {f['portada']} | Descripción: {f['descripcion']} | Paginas: {f['paginas']}"
                    f"| Editorial: {f['editorial']} | Idioma: {f['idioma']} | Enlace: {f['enlace']}")
class Usuario:
    def __init__(self, nombre, edad,tiempo,user,contrasena):
        self.nombre = nombre
        self.edad = edad
        self.tiempo = tiempo
        self.user = user
        self.contrasena = contrasena
    @staticmethod
    def _conn():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_eusuarios INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                edad INTEGER NOT NULL,
                tiempo INTEGER NOT NULL,
                user TEXT NOT NULL UNIQUE,
                contrasena TEXT NOT NULL
            );
        """)
        conn.commit()
        return conn
    def guardar(self):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO usuarios (nombre, edad, tiempo,user,contrasena) VALUES (?, ?, ?,?,?)",
                (self.nombre, self.edad, self.tiempo, self.user, self.contrasena)
            )
        print(f"Usuario '{self.user}' guardado con éxito.")
    @staticmethod
    def listar():
        with Usuario._conn() as conn:
            cur = conn.execute("SELECT * FROM usuarios")
            filas = cur.fetchall()
            if not filas:
                print("No hay usuarios registrados.")
                return
            print("\n--- LISTADO DE USUARIOS ---")
            for f in filas:
                print(
                    f"ID: {f['id_eusuarios']} | Nombre: {f['nombre']} | Edad: {f['edad']} | Tiempo: {f['tiempo']}"
                    f" | Usuario: {f['user']} | Contrasena: {f['contrasena']}")
    @staticmethod
    def login(usuario):
        contrasena = input("Ingrese su contraseña: ").strip()
        with Usuario._conn() as conn:
            cur = conn.execute("SELECT user,contrasena FROM usuarios WHERE user=?", (usuario,))
            fila = cur.fetchone()
            if not fila:
                print("El usuario ingresado no existe.")
                return False
            if contrasena  == fila["contrasena"]:
                print(f"Bienvenido {fila["user"]}")
                return True
            else:
                print("Contraseña incorrecta.")
                return False
def menu():
    print(" ")
    print("Bienvenido al sistema")
    print(" ")
    print("1.Iniciar Sesión")
    print("2.Registrarse")
    print("0.Salir")
    opt = input("Seleccione la opción que desee: ")
    match opt:
        case "1":
            cont = 0
            while cont < 3:
                usuario = input("Ingrese su usuario: ").strip()
                log = Usuario.login(usuario)
                if log == True:
                    menu2(usuario)
                else:
                    cont = cont + 1
            print("Demasiados intentos fallidos, intente denuevo más tarde")
        case "2":
            nombre = input("Ingrese su nombre: ")
            edad = input(int("Ingrese su edad: "))
            tiempo = input(int("Ingrese su tiempo: "))
            user = input("Ingrese su usuario: ")
            contrasena = input("Ingrese su contraseña: ")
            usuario = Usuario(nombre, edad, tiempo,user,contrasena)
            usuario.guardar()
            menu2(user)
        case "0":
            print("Saliendo...")
        case _:
            print("Opción seleccionada no valida")
def menu2(usuario):
    while True:
        print("1.Listar")
        print("2.Registrar libro")
        print("3.Listar libros")
        print("4.Agregar a leídos")
        print("5.Ver leídos")
        print("0.Salir")
        opt = input("Ingrese la opción que desee: ")
        match opt:
            case"1":
                Usuario.listar()
            case"2":
                id = 5678
                titulo = "JJK"
                autores = "Gege "
                categoria = "Shonen"
                portada = "https//url"
                descripcion = "Guerra de heciceros"
                paginas = 300
                editorial = "Norma"
                idioma = "Español"
                enlace = "https//crunchyroll"
                lib = Libro(id, titulo, autores, categoria, portada, descripcion, paginas, editorial, idioma, enlace)
                lib.guardar()
            case"3":
                Libro.listar()
            case"4":
                agregar_leido(usuario,5678)
            case"5":
                listar_leidos(usuario)
            case"0":
                print("Saliendo...")
                break
if __name__ == "__main__":
    lidos()
    menu()