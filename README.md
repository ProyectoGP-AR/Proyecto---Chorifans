# 🔥 ChoriFans – Plataforma de Parrillas, Promociones y Reseñas

Proyecto final de carrera

Autores: **Diego Murgana & Leandro Sosa**  

ChoriFans es una aplicación web construida con **Django + Django Ninja**, pensada para la comunidad choripanera.  
Permite gestionar parrillas, promociones, reseñas, categorías y ubicaciones, con:

- Sitio web completo para que las personas descubran su próximo chori.
- Panel para que los dueños de parrillas respondan reseñas.
- API moderna lista para integrarse con apps móviles o sistemas externos proximamente.

---

## 📑 Tabla de Contenidos

1. [Descripción General](#-descripción-general)  
2. [Características Principales](#-características-principales)  
3. [Tecnologías Utilizadas](#-tecnologías-utilizadas)  
4. [Arquitectura y Estructura del Proyecto](#-arquitectura-y-estructura-del-proyecto)  
5. [Instalación y Configuración](#️-instalación-y-configuración)  
6. [Variables de Entorno](#-variables-de-entorno)  
7. [Base de Datos (Resumen DER)](#-base-de-datos-resumen-der)  
8. [Aplicaciones Internas](#-aplicaciones-internas)  
9. [API (Django Ninja)](#-api-django-ninja)  
10. [Autenticación y Usuarios](#-autenticación-y-usuarios)  
11. [Flujo de Navegación y Funcionalidades](#-flujo-de-navegación-y-funcionalidades)  
12. [Estáticos y Media](#-estáticos-y-media)  
13. [Créditos y Funcionalidades Adicionales](#-créditos-y-funcionalidades-adicionales)  
14. [Comandos Útiles](#-comandos-útiles)  
15. [Próximas Mejoras](#-próximas-mejoras)  
16. [Licencia](#-licencia)  

---

## 📝 Descripción General

ChoriFans es una plataforma gastronómica orientada a la gestión de **parrillas**, **promociones**, **reseñas**, **categorías** y **ubicaciones**.

Incluye:

- Un **backend robusto en Django**.  
- Una **API rápida con Django Ninja**.  
- Un **panel administrador** para gestión interna.  
- Un sitio web con diseño consistente, responsivo y centrado en la experiencia del usuario.

Trabajo Práctico Integrador, cumple los requisitos de:

- Modelado relacional claro (DER).  
- CRUDs completos.  
- Autenticación de usuarios.  
- Módulos adicionales desarrollados por cada integrante del equipo.

---

## 🚀 Características Principales

- Backend en **Django**.  
- API moderna con **Django Ninja** y documentación automática.  
- Sistema de usuarios con **perfil extendido** (avatar, bio, teléfono, rol de dueño de parrilla).  
- CRUD completo para:
  - Parrillas
  - Categorías
  - Ubicaciones
  - Reseñas
  - Promociones
- Sistema de **promociones vigentes** por parrilla.  
- Sistema de **reseñas con ratings** (1 a 5 choripanes).  
- Panel especial para **dueños de parrillas**:
  - Responder reseñas.
  - Valorar la experiencia con emojis (😊 / ☹️).
- Buscador que filtra por:
  - Nombre de parrilla
  - Categoría
  - Ubicación (barrio y ciudad)
- Manejo de archivos estáticos y media (imágenes de parrillas, íconos, etc.).

---

## 🧰 Tecnologías Utilizadas

|   Área    |    Tecnología                   |
|-----------|---------------------------------|
| Backend   | Django                          |
| API       | Django Ninja                    |
| BD        | SQLite (TP)                     |
| Frontend  | Django Templates + HTML5 + CSS3 |
| Estáticos | Django Staticfiles              |
| Media     | File uploads (ImageField)       |
| Entorno   | Python + venv                   |

Detalles extra:

- Sistema de mensajes de Django (`django.contrib.messages`) para feedback amigable.  
- Uso de `ListView`, `DetailView`, `FormView` y `FormMixin` para las vistas principales.  
- Uso de `select_related()` y filtros para optimizar consultas.  
- Estilos centralizados en `static/css/style.css`.  

---

## 🏗 Arquitectura y Estructura del Proyecto

```text
chorifans/
│── manage.py
│── db.sqlite3
│── .env
│── requirements.txt
│── static/
│   └── css/
│       └── style.css
│       └── img/ (logo, decoraciones, verified.png, sin-foto.png, etc.)
│── media/
│── templates/
│   ├── base.html
│   ├── home.html
│   ├── parrillas/
│   ├── categorias/
│   ├── ubicaciones/
│   ├── promociones/
│   ├── resenas/
│   └── accounts/
│── apps/
│   ├── accounts/
│   ├── api/
│   ├── categorias/
│   ├── parrillas/
│   ├── promociones/
│   ├── resenas/
│   └── ubicaciones/
│── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── venv/

-------------------------------

⚙️️ Instalación y Configuración

1️⃣ Clonar repositorio

git clone https://github.com/ProyectoGP-AR/Proyecto---Chorifans.git
cd chorifans

2️⃣ Crear entorno virtual

python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

3️⃣ Instalar dependencias

pip install -r requirements.txt

4️⃣ Configurar .env

Crear un archivo .env en la raíz del proyecto con al menos:

DEBUG=True
SECRET_KEY=tu_clave_super_secreta
DB_NAME=db.sqlite3

5️⃣ Aplicar migraciones

python manage.py migrate

6️⃣ Crear superusuario

python manage.py createsuperuser

7️⃣ Ejecutar servidor

python manage.py runserver

El sitio quedará disponible en:
http://127.0.0.1:8000/

El admin de Django en:
http://127.0.0.1:8000/admin/

🔐 Variables de Entorno

Ejemplo mínimo de configuración:

DEBUG=True
SECRET_KEY=tu_clave_super_secreta
DB_NAME=db.sqlite3

En un entorno real se pueden agregar parámetros para una base de datos externa (PostgreSQL), SMTP, etc.



### 🧱 Base de Datos (Resumen DER)

El modelo respeta una estructura relacional clara:

#### Usuarios y perfiles

- `auth_user` (modelo `User` de Django)
- `accounts_profile`
  - `user` (OneToOne con `auth_user`)
  - `nickname`, `avatar`, `bio`, `telefono`
  - `es_duenio_parrilla` (boolean)
  - `parrilla_asociada` (OneToOne con `parrillas_parrilla`)

#### Parrillas y catálogos

- `parrillas_parrilla`
  - FK a `ubicaciones_ubicacion`
  - FK a `categorias_categoria`
  - `nombre`, `descripcion`, `direccion`, `telefono`, `sitio_web`, `foto_principal`
  - `promedio_puntaje`, `is_active`

- `categorias_categoria`
  - `nombre`, `descripcion`, `is_active`

- `ubicaciones_ubicacion`
  - `barrio`, `ciudad`, `descripcion`, `is_active`

#### Promociones

- `promociones_promocion`
  - FK a `parrillas_parrilla`
  - `titulo`, `descripcion`, `precio_promocional`
  - `fecha_inicio`, `fecha_fin`, `is_active`

#### Reseñas y respuestas

- `resenas_resena`
  - FK a `auth_user` (usuario)
  - FK a `parrillas_parrilla`
  - `puntaje` (1 a 5 choripanes)
  - `comentario`
  - `is_active`
  - `created_at`, `updated_at`
  - **Constraint**: una reseña por usuario y parrilla  
    ```py
    UniqueConstraint(
        fields=["usuario", "parrilla"],
        name="unique_resena_usuario_parrilla",
    )
    ```

- `resenas_respuestaresena`
  - OneToOne con `resenas_resena` (1 respuesta oficial por reseña)
  - FK a `auth_user` (`autor`, dueño de la parrilla)
  - `texto`, `valoracion` (`happy` / `sad`)
  - `created_at`, `updated_at`

---

### 🧩 Aplicaciones Internas

- **accounts**  
  Modelo `Profile` para extender al usuario con datos adicionales y rol de dueño de parrilla.

- **parrillas**  
  Modelo `Parrilla`, vistas de lista, detalle y buscador. Maneja `promedio_puntaje` calculado a partir de reseñas.

- **categorias**  
  Catálogo de categorías de parrillas (feria, gourmet, etc.) con lista y detalle.

- **ubicaciones**  
  Barrios/zonas donde se encuentran las parrillas, con lista y detalle.

- **resenas**  
  Reseñas de usuarios (`Resena`) y respuestas oficiales (`RespuestaResena`). Incluye vistas de:
  - “Mis reseñas”
  - “Valorar reseñas” (para dueños)
  - “Responder reseña / Editar respuesta”

- **promociones**  
  Sistema de promociones vigentes asociadas a parrillas.

- **api**  
  Endpoints con Django Ninja, listados y detalle para integraciones externas.

---

### 🌐 API (Django Ninja)

El proyecto incluye una API moderna construida con **Django Ninja**, que ofrece:

- Endpoints tipados con anotaciones de Python.  
- Validación automática con Pydantic.  
- Serialización de modelos.  
- Documentación OpenAPI/Swagger en `/api/docs`.  
- Endpoint de prueba tipo `/api/ping`.  

Esto permite que ChoriFans pueda conectar fácilmente con aplicaciones móviles o SPA externas.

---

### 👥 Autenticación y Usuarios

Se utilizan los mecanismos estándar de Django:

#### Login / Logout / Registro

- Formularios estilizados con feedback de errores.  
- Énfasis en la **seguridad de la cuenta** (no compartir credenciales).

#### Perfiles (`Profile`)

- Se crea un perfil extendido para cada usuario.  
- Campos extra: `nickname`, `avatar`, `bio`, `telefono`.  
- Campos especiales para dueños de parrilla:
  - `es_duenio_parrilla`
  - `parrilla_asociada`

#### Roles lógicos

- **Visitante (no autenticado)**  
  - Puede navegar, ver parrillas, reseñas y promociones.  
  - No puede dejar reseñas ni responderlas.

- **Usuario registrado común**  
  - Puede dejar **una reseña por parrilla**.  
  - Puede ver y gestionar sus reseñas en “Mis reseñas”.

- **Dueño de parrilla**  
  - Marcado desde el admin mediante `Profile`.  
  - Tiene una `parrilla_asociada`.  
  - Accede al panel “Valorar reseñas”.  
  - Puede responder reseñas y marcar la experiencia como positiva/negativa.  
  - **No puede** dejar reseñas como usuario común (bloqueado en la lógica).

- **Admin / staff**  
  - Acceso al panel de administración de Django.  
  - Gestión completa de datos.

---

### 🧭 Flujo de Navegación y Funcionalidades

#### 🏠 Home

- Presentación del proyecto y menú principal.  
- Grilla de parrillas destacadas.  
- Cards con imagen, nombre, ubicación, categoría y puntaje en choripanes.

#### 🍖 Sección “Parrillas”

- Lista de todas las parrillas en formato **card horizontal**:
  - Imagen principal o imagen de fallback `sin-foto.png`.
  - Nombre, ubicación (barrio + ciudad), categoría.
  - Descripción truncada.
  - Puntaje promedio en choripanes.
  - Botón “Ver más” hacia el detalle.
- Paginación (3 cards por página).

#### 🔎 Sección “Buscar”

- Card principal con buscador centrado.  
- El buscador filtra parrillas por:
  - Nombre
  - Ubicación (barrio o ciudad)
  - Categoría
- Resultados mostrados con el mismo estilo de cards de parrillas.  
- Mensaje claro cuando no hay resultados.

#### 🏷 Sección “Categorías”

- Lista de categorías en cards centradas con título y descripción.  
- En el detalle de una categoría:
  - Descripción de la categoría.
  - Lista de parrillas que pertenecen a esa categoría, con cards horizontales.

#### 📍 Sección “Ubicaciones”

- Lista de ubicaciones con ícono de ubicación (📍) y descripción.  
- En el detalle de una ubicación:
  - Descripción de la zona.
  - Lista de parrillas de ese barrio/ciudad en cards horizontales.

#### 🎫 Sección “Promociones”

- Lista de promociones en formato **ticket/cupón**:
  - Título llamativo.
  - Descripción.
  - Precio promocional destacado.
  - Parrilla asociada (link al detalle).
  - Fechas de vigencia.
- Solo se muestran **promos activas** y dentro de la ventana de fechas.

#### 🧾 Detalle de Parrilla

Incluye:

- Imagen principal (o `sin-foto.png` en tamaño controlado).  
- Datos de contacto, categoría y ubicación.  
- Descripción completa.  
- Puntaje promedio en choripanes.  

**Bloque “Reseñas de la comunidad”:**

- Reseñas con puntaje textual, usuario, fecha y comentario.  
- Si hay respuesta oficial, se muestra una mini-card debajo:
  - Nombre de la parrilla en mayúsculas.
  - Ícono azul de cuenta verificada (`verified.png`).
  - Emoji de valoración (😊 / ☹️).
  - Texto de la respuesta y fecha.

**Bloque “Tu reseña”:**

- Solo visible para usuarios logueados que:
  - No son dueños de parrilla.
  - Todavía no reseñaron esa parrilla.
- Formulario con:
  - Select de puntaje (1–5 choripanes).
  - Textarea de comentario.
  - Botón de publicación.
- Card centrada con estilo consistente.

#### 🔐 Login y Registro

- Formularios simples y claros con diseño oscuro moderno.  
- Mensajes de error bien visibles.  
- Se remarca la importancia de la **seguridad de la cuenta** (credenciales personales, uso responsable).

#### ⭐ Mis reseñas

- Sección privada donde el usuario ve todas las reseñas que publicó.  
- Card grande con listado de reseñas, mostrando:
  - Puntaje, comentario, fecha y parrilla.
- Permite tener una visión rápida de la actividad del usuario.

#### 🧑‍🍳 Valorar reseñas (dueños de parrilla)

- Panel exclusivo para dueños:
  - Lista de reseñas de su `parrilla_asociada`.
  - Card grande para la reseña del usuario (nombre, choripanes, comentario, fecha).
  - Card más chica para la respuesta oficial, con:
    - Nombre de la parrilla + ícono verificado.
    - Emoji de valoración.
    - Texto de respuesta.
- Botón de acción:
  - **Responder reseña** (si no respondió aún).
  - **Editar respuesta** (si ya existe).

- Pantalla de “Responder reseña”:
  - Preview de la reseña del usuario.
  - Toggle de emojis (buena/mala experiencia).
  - Textarea centrada para la respuesta.
  - Botón para guardar cambios y link para volver al panel.

---

### 🎨 Estáticos y Media

- Carpeta `static/`:
  - `static/css/style.css`: hoja de estilos principal.
  - `static/css/img/`: logo, decoraciones, iconos y:
    - `verified.png`: ícono azul de cuenta verificada.
    - `sin-foto.png`: imagen de fallback cuando la parrilla no tiene foto.

- Carpeta `media/`:
  - Lugar donde se guardan las imágenes subidas por usuarios/admin  
    (por ejemplo, fotos de parrillas y avatares).

El CSS unifica el estilo de:

- Cards de parrillas, categorías, ubicaciones y promos.  
- Formularios (login, registro, reseñas, respuestas).  
- Layout del detalle de parrilla.  
- Botones y navegación.

---

### 👨‍💻 Funcionalidades Adicionales

El TP exige que cada integrante implemente al menos una funcionalidad adicional:

## Funcionalidad Adicional de Diego Murgana: Sistema de Promociones por Parrilla

Permite crear promociones especiales asociadas a cada parrilla: fechas de vigencia, precio promocional, descripción y título.  
Incluye frontend, backend y API completa.

---

## 🧩 Modelo

📁 `apps/promociones/models.py`

- Modelo `Promocion`
- Campos:
  - `parrilla` (FK)
  - `titulo`
  - `descripcion`
  - `precio_promocional`
  - `fecha_inicio` / `fecha_fin`
  - `is_active`
  - `created_at`, `updated_at`
- Lógica de vigencia:
  - Una promo es válida si:
    - `is_active == True`
    - `fecha_inicio <= hoy <= fecha_fin`

---

## 🧩 Vistas (Frontend)

📁 `apps/promociones/views.py`  
- Vista para listar promociones del sitio.

📁 `apps/parrillas/views.py`  
- Integración dentro del detalle de la parrilla:
  - Mostrar solo **promociones vigentes**.
  - Ordenar por fecha de finalización.
  - Ocultar cuando no hay promociones disponibles.

---

## 🧩 Templates

📁 `templates/promociones/lista.html`  
- Listado general de promociones activas e inactivas.

📁 `templates/parrillas/detalle.html`  
- Sección **“Promociones vigentes”** dentro de cada parrilla.

---

## 🧩 API REST – Endpoints

📁 `apps/api/api.py`  

CRUD completo:

- `GET /api/promociones`
- `GET /api/promociones/{id}`
- `POST /api/promociones` *(protegido con `SessionAuth`)*
- `PUT /api/promociones/{id}` *(protegido)*
- `DELETE /api/promociones/{id}` *(protegido)*

Además:

### Query Param

- `GET /api/promociones?solo_activas=true` → devuelve solo promociones vigentes.

### Endpoint extra

- `GET /api/promociones/activas` → muestra únicamente promociones válidas según fecha.

---

# 🎯 Impacto de la funcionalidad

- Añade complejidad relacionada con fechas, vigencia y lógica de negocio.  
- Integra modelo, vistas, templates y API REST.  
- Permite enriquecer la experiencia del usuario mostrando promos reales.

---

## Funcionalidad Adicional de Leandro Sosa: Sistema de Valoración y Respuesta de Reseñas para Dueños de Parrillas

Permite que los dueños oficiales de una parrilla respondan las reseñas que reciben, valorando la experiencia del cliente (positiva/negativa) y mostrando una respuesta pública “verificada” tanto en el panel del dueño como en el detalle de la parrilla.

Incluye cambios en modelos, vistas, templates, lógica de permisos y flujo de navegación.

---

## 🧩 Modelo

📁 `apps/accounts/models.py`

- Modelo `Profile` (extiende al usuario de Django):
  - `user` (OneToOne con `auth_user`)
  - Campos generales: `nickname`, `avatar`, `bio`, `telefono`
  - Campos especiales para dueños de parrilla:
    - `es_duenio_parrilla` (boolean)
    - `parrilla_asociada` (OneToOne con `parrillas_parrilla`)
  - Lógica de rol:
    - Un perfil marcado como `es_duenio_parrilla=True` y con `parrilla_asociada` se considera **dueño oficial** de esa parrilla dentro del sitio.

📁 `apps/resenas/models.py`

- Modelo `Resena`
  - `usuario` (FK a `auth_user`)
  - `parrilla` (FK a `parrillas_parrilla`)
  - `puntaje` (1 a 5 choripanes)
  - `comentario`
  - `is_active`
  - `created_at`, `updated_at`
  - Restricción:
    - `UniqueConstraint(fields=["usuario", "parrilla"], name="unique_resena_usuario_parrilla")`  
      → una sola reseña por usuario y parrilla.

- Modelo `RespuestaResena`
  - `resena` (OneToOne con `Resena`)  
    → garantiza **una única respuesta oficial por reseña**.
  - `autor` (FK a `auth_user`)  
    → debe ser el dueño de la parrilla asociada a esa reseña.
  - `texto` (respuesta pública de la parrilla)
  - `valoracion` (`"happy"` / `"sad"` → 😊 / ☹️)
  - `created_at`, `updated_at`

---

## 🧩 Vistas (Frontend)

📁 `apps/resenas/views.py`

- Vista **“Valorar reseñas”**:
  - Lista las reseñas asociadas a la `parrilla_asociada` del dueño logueado.
  - Solo accesible para usuarios cuyo `Profile.es_duenio_parrilla` está activo.
  - Cada reseña muestra:
    - Usuario, puntaje en choripanes, comentario, fecha y parrilla.
    - Si existe respuesta oficial → mini-card con respuesta.
    - Si no existe → mensaje de “pendiente de respuesta”.
  - Botón de acción:
    - “Responder reseña” si todavía no respondió.
    - “Editar respuesta” si la respuesta ya existe.

- Vista **“Responder reseña / Editar respuesta”**:
  - Recibe una reseña concreta.
  - Verifica que el usuario logueado sea dueño de la `parrilla` de esa reseña.
  - Si ya hay `RespuestaResena`:
    - Carga datos iniciales para edición.
  - Si no hay:
    - Crea una nueva respuesta.
  - Maneja:
    - `valoracion` (toggle de emojis 😊 / ☹️).
    - `texto` (campo de respuesta centrado).
  - Redirige al panel de “Valorar reseñas” tras guardar.

📁 `apps/parrillas/views.py`

- Vista **`ParrillaDetailView`**:
  - Bloquea que los **dueños de parrilla** dejen reseñas como usuarios comunes.
  - Calcula flags de contexto:
    - `es_duenio_parrilla`
    - `ya_reseño`
    - `puede_reseñar`
  - En el contexto de reseñas:
    - Incluye la relación hacia `RespuestaResena` para poder mostrar respuestas oficiales debajo de cada reseña.

---

## 🧩 Templates

📁 `templates/resenas/valorar_resenas.html`

- Panel para dueños:
  - Card grande con la reseña del usuario (nombre, choripanes, comentario, fecha, parrilla).
  - Card más chica con la **respuesta de la parrilla**, cuando existe:
    - Nombre de la parrilla en mayúsculas.
    - Ícono azul **verified** junto al nombre.
    - Emoji de valoración (😊 / ☹️).
    - Texto de la respuesta y fecha de actualización.
  - Botón central:
    - “Responder reseña” / “Editar respuesta”.

📁 `templates/resenas/responder_resena.html`

- Pantalla para responder o editar:
  - Preview de la reseña original, con mismo estilo que el panel.
  - Formulario de respuesta:
    - Toggle de emojis para `valoracion` (buena/mala experiencia).
    - Textarea centrada para `texto`.
  - Botones:
    - Guardar cambios.
    - Volver al panel de “Valorar reseñas”.

📁 `templates/parrillas/detalle.html`

- Dentro de **“Reseñas de la comunidad”**:
  - Debajo de cada reseña se muestra, si existe:
    - Mini-card de **respuesta oficial** de la parrilla:
      - Nombre en mayúsculas.
      - Ícono azul de cuenta verificada (`verified.png`).
      - Emoji de valoración (😊 / ☹️).
      - Texto de respuesta + fecha.
- En el bloque **“Tu reseña”**:
  - Formulario solo visible para usuarios que:
    - Están logueados.
    - No son dueños de parrilla.
    - No hayan reseñado esa parrilla antes.


## 🧩 API REST – Endpoints

📁 `apps/api/api.py`

Además de los endpoints generales de reseñas, la lógica de **respuesta de reseñas por dueños** se apoya principalmente en el frontend (templates y vistas).  
A nivel de API se dispone de:

- `GET /api/resenas`
- `GET /api/resenas/{id}`
- `POST /api/resenas` *(usuario autenticado: crear reseña)*

Opcionalmente (según configuración del TP) se pueden exponer:

- `GET /api/parrillas/{id}/resenas` → listar reseñas de una parrilla.
- `GET /api/usuarios/{id}/resenas` → listar reseñas de un usuario.

> La edición y gestión de `RespuestaResena` se resuelven desde las vistas HTML (panel de dueños), sin necesidad de exponer un CRUD público para respuestas oficiales.

---

# 🎯 Impacto de la funcionalidad

  - Agrega un **nuevo rol lógico** (dueño de parrilla) que interactúa de forma distinta con el sistema.  
  - Conecta varias capas:
  - Extensión de usuario (`Profile`).
  - Nuevos modelos (`RespuestaResena`).
  - Reglas de negocio (un dueño no puede reseñar, solo responder).
  - Vistas protegidas para panel de dueños.
  - Templates específicos para panel y respuestas oficiales.
  - Mejora la experiencia de usuario:
  - Los clientes ven respuestas oficiales con ícono verificado y emoji de valoración.
  - Los dueños pueden gestionar su reputación y contestar comentarios.

---

### 🛠 Comandos Útiles

| Acción              | Comando                                |
|---------------------|----------------------------------------|
| Ejecutar servidor   | `python manage.py runserver`           |
| Aplicar migraciones | `python manage.py migrate`             |
| Crear superusuario  | `python manage.py createsuperuser`     |
| Crear app nueva     | `python manage.py startapp nombre_app` |

---

### 🚧 Próximas Mejoras

- Dockerización del proyecto.  
- Reemplazo de SQLite por PostgreSQL.  
- Autenticación con **JWT** en la API.  
- Tests automatizados con `pytest` o `unittest`.  
- Panel de administración mejorado para dueños (subir fotos, gestionar promos).



MIT License

Copyright (c) 2025 D&L

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
