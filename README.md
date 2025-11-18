# 🔥 Chorifans – Plataforma de Parrillas, Promociones y Reseñas

Aplicación web construida con **Django + Django Ninja**, diseñada para gestionar parrillas, promociones, reseñas, ubicaciones y usuarios mediante un panel administrativo y una API moderna, ideal para integrarse con aplicaciones móviles o sistemas externos.

## 📑 Tabla de Contenidos

1. Descripción General
2. Características Principales
3. Tecnologías Utilizadas
4. Arquitectura y Estructura del Proyecto
5. Instalación y Configuración
6. Variables de Entorno
7. Base de Datos
8. Aplicaciones Internas
9. API (Django Ninja)
10. Autenticación y Usuarios
11. Estáticos y Media
12. Comandos Útiles
13. Próximas Mejoras
14. Licencia

---

## 📝 Descripción General

ChoriFans es una plataforma gastronómica orientada a la gestión de parrillas, promociones, reseñas, categorías y ubicaciones.  
Incluye un backend robusto en Django, una API rápida con Django Ninja y un panel administrador para gestión interna.

---

## 🚀 Características Principales

- Backend en Django 4.x  
- API moderna con Django Ninja  
- Sistema de usuarios y perfiles  
- CRUD completo para todos los módulos  
- Sistema de promociones  
- Reseñas con ratings  
- Ubicaciones geográficas  
- Archivos static y media configurados  

---

## 🧰 Tecnologías Utilizadas

|   Área    |    Tecnología    |
|-----------|------------------|
|  Backend  |      Django      |
|     API   |   Django Ninja   |
|     BD    |      SQLite      |
|  Frontend | Django Templates |
| Estáticos |    Staticfiles   |
|   Media   |   File uploads   |
|  Entorno  |    Python venv   |

---

## 🏗 Arquitectura y Estructura del Proyecto

```
chorifans/
│── manage.py
│── db.sqlite3
│── .env
│── static/
│── media/
│── templates/
│── apps/
│   ├── accounts/
│   ├── api/
│   ├── categorias/
│   ├── parrillas/
│   ├── promociones/
│   ├── resenas/
│   ├── ubicaciones/
│── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── venv/
```

---

## ⚙️ Instalación y Configuración

### 1️⃣ Clonar repositorio

```
git clone https://github.com/ProyectoGP-AR/Proyecto---Chorifans.git
cd chorifans
```

### 2️⃣ Crear entorno virtual

```
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate       # Windows
```

### 3️⃣ Instalar dependencias

```
pip install -r requirements.txt
```

### 4️⃣ Configurar .env

### 5️⃣ Migraciones

```
python manage.py migrate
```

### 6️⃣ Crear superusuario

```
python manage.py createsuperuser
```

### 7️⃣ Ejecutar servidor

```
python manage.py runserver
```

---

## 🔐 Variables de Entorno

Ejemplo:

```
DEBUG=True
SECRET_KEY=tu_clave
DB_NAME=db.sqlite3
```

---

## 🧱 Aplicaciones Internas

- accounts  
- parrillas  
- categorias  
- promociones  
- resenas  
- ubicaciones  
- api  

---

## 🌐 API (Django Ninja)

El proyecto incluye una API moderna construida con **Django Ninja**, que genera documentación automática y soporta:

- Validación con Pydantic
- Tipado estático
- Serialización automática
- Documentación OpenAPI/Swagger

## 🧑‍💻 Autenticación y Usuarios

- Perfiles con avatar  
- Grupos y permisos  
- AdminPanel configurado  

---

## 🎨 Estáticos y Media

```
static/
media/
```

---

## 🛠 Comandos Útiles

|      Acción        |              Comando             |
|--------------------|----------------------------------|
|  Ejecutar servidor |    python manage.py runserver    |
|     Migraciones    |     python manage.py migrate     |
| Crear superusuario | python manage.py createsuperuser |

---

## 🚧 Próximas Mejoras

- Dockerización  
- JWT en API  
- PostgreSQL  
- Testing  

---

## 🪪 Licencia

```
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
```

