# BibliotecaAR Backend

MVP en Django + Django REST Framework + SQLite para administrar libros/cuentos y escenas de BibliotecaAR.

## Desarrollo

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py createsuperuser
.\.venv\Scripts\python manage.py runserver 0.0.0.0:8000
```

## Deploy en Render

Este repo incluye `render.yaml` y `build.sh`.

En Render crea un Web Service desde GitHub y usa:

```bash
Build Command: bash build.sh
Start Command: gunicorn config.wsgi:application
```

Variables de entorno recomendadas:

```text
DEBUG=False
SECRET_KEY=<generada por Render>
ALLOWED_HOSTS=<tu-servicio>.onrender.com
CSRF_TRUSTED_ORIGINS=https://<tu-servicio>.onrender.com
CORS_ALLOWED_ORIGINS=https://<tu-frontend-vercel>.vercel.app
SERVE_MEDIA_FILES=True
SECURE_SSL_REDIRECT=True
```

Si luego conectas un frontend en Vercel, agrega su dominio a `CSRF_TRUSTED_ORIGINS`.

Nota: en el plan gratis de Render, los archivos subidos en `media/` pueden no ser persistentes despues de redeploys. Para demo esta bien; para datos importantes conviene Cloudinary o un disco persistente.

## Modelo inicial

- `Book`: portada, titulo, descripcion y estado publicado.
- `Scene`: texto, audio opcional, modelo `.glb` opcional, `prefab_key`, `qr_code` y `qr_image`.

El QR se genera automaticamente cuando se guarda una escena.

## Endpoint para Unity

```http
GET /api/unity/scenes/<qr_code>/
```

Solo devuelve escenas cuyo libro esta publicado.

La respuesta incluye `glb_model_url` cuando la escena tiene un modelo `.glb` cargado en el admin.

## API para docente

Requiere un usuario `is_staff=True`.

```http
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
GET /api/auth/me/

GET /api/teacher/books/
POST /api/teacher/books/
GET /api/teacher/books/<id>/
PATCH /api/teacher/books/<id>/
DELETE /api/teacher/books/<id>/

GET /api/teacher/scenes/
POST /api/teacher/scenes/
GET /api/teacher/scenes/<id>/
PATCH /api/teacher/scenes/<id>/
DELETE /api/teacher/scenes/<id>/
```

Usa `multipart/form-data` para subir `cover`, `audio` o `glb_model`.

Si no existe ningun docente, `POST /api/auth/register/` permite crear la primera cuenta docente. Despues de eso, solo un docente autenticado puede crear otras cuentas docentes.
