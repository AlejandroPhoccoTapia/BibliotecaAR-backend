# BibliotecaAR Backend

MVP en Django + Django REST Framework + SQLite para administrar libros/cuentos y escenas de BibliotecaAR.

## Desarrollo

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py createsuperuser
.\.venv\Scripts\python manage.py runserver 0.0.0.0:8000
```

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
