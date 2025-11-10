Descripción
Aplicación web para administrar lecturas de usuarios con estados Por leer, Leyendo y Leídos. Incluye un planificador que genera sesiones de lectura según horas libres del usuario.

Estructura del proyecto
assets/

css/: estilos globales.

js/: lógica por vista y módulos:

login.js: autenticación y validaciones.

registrar.js: alta de usuarios.

menu.js: navegación entre secciones y control del header.

perfil.js: edición de perfil y disponibilidad de horas.

porleer.js: gestión de backlog “Por leer”.

leidos.js: historial y métricas de libros terminados.

programa.js: generación y visualización del plan de lectura.

img/

logo_biblioteca.png: marca y favicon si se usa.

paginas/

home.html: landing o dashboard.

login.html: inicio de sesión.

registrar.html: registro de usuario.

perfil.html: perfil y configuración (horas libres).

misLibros.html: vista principal con tabs Por leer, Leyendo, Leídos.

recomen.html: recomendaciones (si aplica).

python/

Backend.py: API y persistencia.

.venv/: entorno virtual Python.

Requisitos
Python 3.10+ y pip.

Entorno virtual recomendado (.venv).

Navegador moderno (ES6+).

Instalación y ejecución
Crear entorno e instalar dependencias:

python -m venv .venv

En Windows: .venv\Scripts\activate

En macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt

Ejecutar backend:

python python/Backend.py

Servir front-end:

Opción simple: abrir paginas/home.html con Live Server o un servidor estático.

Opción integrada: si Backend.py sirve archivos estáticos, acceder a http://localhost:PUERTO/.

Configuración
Variables de entorno sugeridas: PORT, DB_URL o ruta de archivo JSON, TZ/LOCALE.

Archivo .env opcional para desarrollo.

Uso básico
Registrar e iniciar sesión.

En perfil, ver libros leyendo.

En el icono del libro, ver libros leidos

en el icono del reloj, ver libros Por Leer

Front-end estático en paginas/ con JS modular en assets/js/.

Backend.py expone endpoints para usuarios, libros, estados y planes. Persistencia en archivo o DB según configuración.

Módulos front-end

perfil.js: CRUD de libros leyendo.

porleer.js y leidos.js: listas.

programa.js: cálculo/visualización de plan (divide páginas o duración según horas libres y velocidad).

login.js y registrar.js: sesión y almacenamiento de token

Modelo de datos (sugerido)
Usuario: id, nombre, contraseña, disponibilidad{horas}.

Libro: id, titulo, autor, paginas, categoria, paginas, editoria.

Plan: horas disponibles y libro agregado

Backend
Endpoints (nombres tentativos):

POST /auth/login, POST /auth/register

GET/POST /usuarios/{id}/disponibilidad

POST/GET /libros, PATCH /libros/{id}/estado

POST /libros/{id}/plan, GET /libros/{id}/plan

POST /libros/{id}/progreso
asta completar; recalcular al cambiar disponibilidad.

leidos.js: resumen de lectura, fechas y duración real vs. estimada.
