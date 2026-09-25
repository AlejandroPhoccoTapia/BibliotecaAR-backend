# BibliotecaAR — Backend y API

Backend de una plataforma educativa de tesis que vincula libros y capítulos con contenido de realidad aumentada mediante códigos QR. Es la fuente de datos y archivos para el panel docente y la aplicación Android.

Documentación contrastada con el código el **24 de septiembre de 2026**. Es un MVP: implementación no equivale a validación en producción, precisión biométrica demostrada ni resultados pedagógicos evaluados.

## 1. Contexto del proyecto completo

| Repositorio | Responsabilidad |
| --- | --- |
| [BibliotecaAR](https://github.com/AlejandroPhoccoTapia/BibliotecaAR) | Unity Android: escaneo QR, seguimiento de imágenes, modelos 3D, texto y audio. |
| [BibliotecaAR-backend](https://github.com/AlejandroPhoccoTapia/BibliotecaAR-backend) | Este repositorio: Django, API, sesiones docentes, catálogo, estudiantes, QR y almacenamiento. |
| [BiblitoecaAR-fronted](https://github.com/AlejandroPhoccoTapia/BiblitoecaAR-fronted) | Panel docente React. El enlace conserva la grafía actual del repositorio. |

```text
Docente -> React -> API Django -> SQLite local / PostgreSQL en Supabase
                        |
                        +-> archivos locales / Supabase Storage
                        |
Android Unity -- QR --> GET /api/unity/scenes/<qr_code>/
              <-- texto y URLs de audio, GLB e imagen QR
```

El docente crea un libro, añade capítulos con recursos, publica el libro y obtiene sus QR. Unity lee un QR, consulta la API y coloca el contenido 3D sobre la imagen reconocida.

**Vocabulario:** un «capítulo» del panel es un registro `Scene` de Django. No es una escena Unity: `QRScanScene` y `ARScene` son las pantallas del cliente móvil. El QR contiene un identificador, no una URL. `prefab_key` identifica un recurso local Unity; `glb_model` es un archivo descargable.

## 2. Tecnologías y estructura

Versiones fijadas en [requirements.txt](requirements.txt): Django 6.0.7, Django REST Framework 3.17.1, Pillow, qrcode, dj-database-url, psycopg, django-storages/boto3, django-cors-headers, WhiteNoise y Gunicorn.

```text
catalog/
  models.py             Book, Scene, StudentProfile; generación de QR
  serializers.py        Contratos y generación de firma facial al recibir foto
  views.py              Autenticación, CRUD, identificación y consulta Unity
  urls.py               Router y endpoints
  face_recognition.py   Extracción LBP y comparación de imágenes
  admin.py              Administración Django y vistas previas
  migrations/           0001 catálogo; 0002 GLB; 0003 estudiantes
  signals.py            Limpieza de archivos después del commit de base de datos
  validators.py         Límites de subida y validación de cabecera GLB
  tests.py / test_*.py   40 pruebas de backend y regresiones
config/
  settings.py           Entorno, base de datos, sesiones, CORS y almacenamiento
  test_settings.py      SQLite en memoria, media temporal y caché aislada
  storage_backends.py   Construcción de URLs públicas Supabase
  urls.py               /admin/, /api/ y media de desarrollo
  wsgi.py / asgi.py      Entradas de servidor
manage.py
build.sh                Instala dependencias, collectstatic y migrate
render.yaml             Despliegue previsto en Render
```

## 3. Modelo y reglas de negocio

| Entidad | Datos y relaciones |
| --- | --- |
| `Book` | `title`, `description`, `cover`, `is_published`, fechas; tiene muchas escenas. |
| `Scene` | `book`, `title`, `order`, `text`, `audio`, `glb_model`, `prefab_key`, `qr_code`, `qr_image`, fechas. |
| `StudentProfile` | `full_name`, `classroom`, `photo`, `face_signature` JSON, `assigned_books` muchos-a-muchos, `is_active`, fechas. |
| Usuario Django | Es docente cuando `is_staff=True`; no hay modelo docente separado. |

- `text` y `prefab_key` son obligatorios al crear escenas, incluso con GLB. La API admite título de escena vacío, aunque el panel exige título.
- `order` organiza capítulos; la API exige al menos 1. No hay unicidad de orden dentro de un libro.
- `Scene.save()` genera un código basado en el título del libro y un fragmento UUID si falta. Genera el PNG al crear el QR o cambiar su código. Renombrar un libro no cambia un código existente.
- Eliminar un libro elimina sus escenas por cascada.
- Todos los docentes autorizados comparten catálogo y estudiantes: no hay aislamiento por docente/institución.
- `StudentProfile` es un perfil, no un usuario Django con sesión.

## 4. Desarrollo local

Requisitos: Python compatible con Django 6.0 (3.12 o superior), pip y Git. Desde este repositorio, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py createsuperuser
.\.venv\Scripts\python manage.py runserver 0.0.0.0:8000
```

El superusuario puede usar `http://127.0.0.1:8000/admin/` y el panel docente. Alternativamente, omitir `createsuperuser` y registrar el primer docente desde el panel si todavía no existe ningún staff. No hay datos precargados ni contraseña por defecto.

Sin `DATABASE_URL`, se usa `db.sqlite3`; sin Supabase Storage, se guardan archivos en `media/`. Iniciar el frontend en otra terminal según su README. Para Unity en un teléfono, usar la IP LAN del ordenador, la misma red y permitir el puerto 8000 en el firewall; `localhost` en Android apunta al propio teléfono.

**No se cargan archivos `.env` automáticamente.** Settings lee `os.environ`. Definir variables en PowerShell, por ejemplo `$env:DEBUG = 'True'`, antes de ejecutar Django.

## 5. Autenticación y permisos

Se usan sesiones Django con cookies. El panel envía `credentials: 'include'` y `X-CSRFToken` para escrituras; obtiene `csrf_token` del JSON de sesión/autenticación y contempla la cookie como respaldo.

| Método y ruta | Comportamiento |
| --- | --- |
| `GET /api/auth/me/` | Devuelve `is_authenticated`, `csrf_token` y datos de usuario si existe sesión. |
| `POST /api/auth/login/` | Recibe `username` y `password`; exige usuario staff válido. |
| `POST /api/auth/register/` | Recibe `username`, `password` (mínimo 8), `first_name` y `last_name` opcionales. |
| `POST /api/auth/logout/` | Requiere autenticación y cierra sesión. |

Si no existe ningún staff, el registro admite al primer docente sin sesión e inicia su sesión. Después exige un docente autenticado y conserva su sesión al crear otra cuenta. La respuesta incluye `created_user` con el ID y nombre de usuario de la cuenta creada, además de los datos de la sesión actual. Se validan el formato del nombre de usuario y los validadores de contraseña de Django configurados en settings.

Login y registro exigen CSRF también sin sesión: obtener primero el token con `GET /api/auth/me/` y enviar la cookie y `X-CSRFToken`. Login, registro e identificación facial tienen límites de solicitudes configurables. Usan la caché Django; la caché local por proceso no coordina varios workers. Para ese despliegue se necesita una caché compartida; estos límites no sustituyen protección contra abuso en el servidor de entrada.

CRUD docente: `IsAdminUser`. Consulta Unity: pública, limitada por publicación. Identificación facial: pública, **no crea sesión ni emite token**. No hay un sistema JWT implementado.

## 6. CRUD y archivos

| Colección | Campos de entrada |
| --- | --- |
| `/api/teacher/books/` | `title`, `description`, `is_published`, `cover`. |
| `/api/teacher/scenes/` | `book` (ID), `title`, `order`, `text`, `prefab_key`, `audio`, `glb_model`. |
| `/api/teacher/students/` | `full_name`, `classroom`, `photo`, `assigned_books` (IDs), `is_active`. |

Colecciones: GET/POST. Detalles como `/api/teacher/books/1/`: GET/PUT/PATCH/DELETE. El panel edita libros/escenas con PATCH y envía el perfil completo de estudiantes con PUT. Los listados devuelven arreglos sin paginación.

Usar multipart para archivos y JSON para cambios sin archivos. En multipart, enviar asignaciones como valores repetidos `assigned_books=1`, `assigned_books=2`, no la cadena `"1,2"`. Para vaciar asignaciones en un cambio sin foto, usar JSON `{"assigned_books": []}`. En un PUT multipart completo, omitir `assigned_books` vacía la relación; en PATCH, omitirlo conserva las asignaciones. Las cadenas vacías permiten limpiar campos opcionales. Estas combinaciones tienen pruebas de regresión.

Respuestas adicionales:
- Libros: `cover_url`, `scenes_count`, fechas.
- Escenas: `book_title`, `audio_url`, `glb_model_name`, `glb_model_url`, `qr_code`, `qr_image_url`, fechas. El QR es de solo lectura en esta API.
- Estudiantes: `photo_url`, `assigned_books_detail`, `has_face_signature`, fechas; la firma no se expone mediante este serializer.

PATCH de escena admite `{"remove_glb_model": true}` y el panel tiene un control para enviarlo. La API comprueba extensión `.glb`, cabecera GLB v2 y longitud declarada, además del tamaño máximo. No valida todos los chunks ni la compatibilidad del modelo con Unity. Audio admite `.mp3`, `.wav`, `.ogg`, `.m4a`, `.aac` y `.flac`; comprueba extensión y tamaño, sin decodificar el contenido. Las imágenes pasan por ImageField y un límite de tamaño. Estas validaciones pertenecen a los serializers de la API; no se aplican automáticamente a escrituras directas por ORM/admin.

Portadas, audio, GLB, QR y fotos sustituidos o eliminados se borran del storage después de confirmar la transacción. Las señales cubren cascadas y `QuerySet.delete()` y conservan nombres todavía referenciados por otro campo de media gestionado. Un fallo del storage se registra sin deshacer una operación ya confirmada; no hay cola automática de reintentos. Los archivos nuevos subidos antes de un rollback pueden quedar huérfanos porque el storage no es transaccional. Tampoco se limpian huérfanos antiguos ni se interceptan `QuerySet.update()`/`bulk_update()`.

## 7. Contrato Unity

```http
GET /api/unity/scenes/<qr_code>/
```

404 si el código no existe o el libro no está publicado. Ejemplo ilustrativo:

```json
{
  "qr_code": "libro-demo-scene-a1b2c3d4e5",
  "book_title": "Libro demo",
  "title": "La hormiga",
  "order": 1,
  "text": "Texto narrativo del capítulo.",
  "prefab_key": "Hormiga",
  "cover_url": null,
  "audio_url": "https://media.example/scenes/audio/hormiga.mp3",
  "glb_model_url": "https://media.example/scenes/models/hormiga.glb",
  "qr_image_url": "https://media.example/scenes/qr/libro-demo-scene-a1b2c3d4e5.png"
}
```

Archivos ausentes: `null`. Unity espera estos nombres en `UnitySceneApiResponse`. El backend no convierte modelos a GLB ni sintetiza voz; los recursos se suben preparados. Unity descarga también el QR para añadirlo a su biblioteca de seguimiento.

## 8. Identificación facial: alcance real

`POST /api/student/face-login/` recibe multipart con `image`. Devuelve `student` (ID, nombre, aula, foto y libros asignados), `distance` y `confidence`; 400 para entrada inválida y 404 si no hay coincidencia aceptada.

Proceso de `face_recognition.py`:
1. Leer imagen con Pillow.
2. Intentar detección Haar con OpenCV/NumPy si están instalados.
3. Sin esas librerías o sin detección, usar un recorte central; no se rechaza necesariamente una imagen sin rostro.
4. Escala de grises, 128 × 128, ecualización.
5. Histograma LBP de 256 valores: 4 × 4 celdas, 16 bins por celda.
6. Comparar con perfiles activos mediante distancia chi-cuadrado; elegir la menor distancia aceptada por el umbral `0.45` de settings.

`confidence = max(0, 1 - distance / threshold)` es un cálculo heurístico, no una probabilidad calibrada. OpenCV/NumPy no están en `requirements.txt`; la instalación base recurre al recorte central. No hay detección de vida ni evaluación de precisión con rostros reales en las pruebas.

La firma se calcula en el serializer al subir foto por API y se borra al enviar `photo: null`. Crear perfiles directamente por ORM o admin no ejecuta ese serializer. La comparación rechaza firmas malformadas o no normalizadas, y la vista omite esos perfiles. Unity no consume este endpoint todavía. La respuesta de identificación incluye solo libros asignados publicados; el endpoint Unity no exige identidad ni comprueba asignaciones. Identificación y autorización no están integradas.

## 9. Entorno y despliegue previsto

Render sirve Django; Supabase PostgreSQL guarda datos y Supabase Storage compatible con S3 guarda archivos. El manifiesto no acredita que esos servicios estén actualmente operativos.

| Variable | Uso / valor por defecto |
| --- | --- |
| `DEBUG` | `True` local; configurar `False` en producción. |
| `SECRET_KEY` | Clave Django. Render genera una; no usar la clave de desarrollo en producción. |
| `ALLOWED_HOSTS` | Hosts separados por comas; `*` por defecto local. |
| `CSRF_TRUSTED_ORIGINS` | Orígenes completos adicionales; localhost/127.0.0.1:5173 y :5174 ya están contemplados. |
| `CORS_ALLOWED_ORIGINS` | Orígenes web separados por comas; vacío por defecto. |
| `DATABASE_URL` | PostgreSQL; si falta, SQLite. |
| `DB_SSL_REQUIRE` | `True` por defecto para conexión por URL. |
| `MEDIA_ROOT` | Directorio local; por defecto `media/`. |
| `SERVE_MEDIA_FILES` | Rutas de desarrollo; por defecto sigue DEBUG. No sustituye un servidor de media en producción. |
| `USE_SUPABASE_STORAGE` | `False` local; `True` para Supabase S3. |
| `SUPABASE_STORAGE_BUCKET_NAME` | Por defecto `media`. |
| `SUPABASE_STORAGE_ENDPOINT_URL` | `https://<project-ref>.supabase.co/storage/v1/s3`. |
| `SUPABASE_STORAGE_PUBLIC_URL` | `https://<project-ref>.supabase.co/storage/v1/object/public/media`. |
| `SUPABASE_STORAGE_ACCESS_KEY_ID` | Credencial S3 del servidor. |
| `SUPABASE_STORAGE_SECRET_ACCESS_KEY` | Secreto S3 del servidor. |
| `SUPABASE_STORAGE_REGION_NAME` | Por defecto `us-east-1`. |
| `SECURE_SSL_REDIRECT` | Redirección HTTPS con DEBUG=False; activada en render.yaml. |
| `TEACHER_LOGIN_RATE` | Límite DRF de login; `20/minute`. |
| `TEACHER_REGISTER_RATE` | Límite DRF de registro; `10/hour`. |
| `STUDENT_FACE_RATE` | Límite DRF de identificación facial; `30/minute`. |
| `MAX_IMAGE_UPLOAD_BYTES` | Imágenes: `10485760` (10 MiB). |
| `MAX_AUDIO_UPLOAD_BYTES` | Audio: `52428800` (50 MiB). |
| `MAX_GLB_UPLOAD_BYTES` | Modelos GLB: `104857600` (100 MiB). |

Render ejecuta `bash build.sh` para instalar dependencias, recolectar estáticos y migrar, y `gunicorn config.wsgi:application` para servir. Configurar base, bucket y credenciales en el entorno; comprobar los dominios incluidos en `render.yaml`.

Con DEBUG=False, cookies de sesión/CSRF usan Secure y SameSite=None. Configurar HTTPS y el dominio del panel en CORS y CSRF; las políticas del navegador sobre cookies entre sitios también influyen.

WhiteNoise sirve estáticos, no sustituye el almacenamiento de subidas. `SupabaseMediaStorage.url()` forma URLs públicas; las fotos de estudiantes también usan ese storage, sin un bucket privado separado. La privacidad de esas fotos necesita un diseño adicional si se requiere acceso restringido.

Si no se usa Supabase, configurar explícitamente persistencia y servicio de media. La función Django `static()` no sirve media con DEBUG=False, incluso con SERVE_MEDIA_FILES=True. No asumir persistencia de archivos locales en un despliegue efímero.

## 10. Validación

Usar la configuración de pruebas: fuerza SQLite en memoria, archivos temporales y caché local. No usarla para servir la aplicación: también simplifica el hash de contraseñas para acelerar la suite.

```powershell
.\.venv\Scripts\python manage.py check --settings=config.test_settings
.\.venv\Scripts\python manage.py test catalog --settings=config.test_settings
.\.venv\Scripts\python manage.py makemigrations --check --dry-run --settings=config.test_settings
```

Las **40 pruebas pasan** con Python 3.12.14. Cubren QR, publicación, consulta Unity, permisos, CSRF anónimo, sesiones, registro, límites de solicitudes, estudiantes, contratos multipart/PUT/PATCH, validación de subidas y limpieza de media con rollback, cascadas y referencias compartidas. `makemigrations --check --dry-run` no detecta cambios de esquema. Usan archivos sintéticos y dibujos; no validan biometría real, AR, modelos 3D reales, cookies entre dominios ni Supabase.

Prueba integral: iniciar los tres componentes, crear libro publicado y capítulo con recursos, comprobar JSON/URLs, configurar Unity, escanear en Android y verificar texto/audio/modelo. Despublicar el libro debe producir 404 en la API; el fallback local de Unity puede mostrar demostraciones para códigos conocidos. Probar estudiantes por separado hasta integrar su flujo móvil.

## 11. Problemas conocidos

- No hay autorización por estudiante, progreso lector, evaluaciones ni estadísticas de aprendizaje persistidas.
- La validación de cabecera GLB no garantiza un modelo utilizable y el audio no se decodifica; una subida aceptada puede fallar en Unity.
- El storage no es transaccional: quedan pendientes reconciliación de huérfanos y reintentos de borrados fallidos.
- Sin paginación, aislamiento por docente ni indexación biométrica: se comparan todos los perfiles activos con firma.
- El alta pública inicial no serializa registros concurrentes del primer docente.
- Las fotos usan URLs públicas y los límites de solicitudes requieren caché compartida para coordinar varios workers.

## 12. Guía para el siguiente asistente

1. Leer los tres README y contrastarlos con el código vigente; esta guía es una fotografía del estado.
2. Revisar `git status` en cada repositorio independiente y conservar cambios ajenos.
3. Empezar por modelos, serializers y vistas. Para integración comparar `catalog/urls.py`, `src/api.js` del panel y `ARSceneController.cs` de Unity.
4. Mantener nombres JSON y significado del QR; actualizar consumidores y pruebas si cambia el contrato.
5. No presentar la identificación facial como autenticación completa ni asumir que las asignaciones restringen QR.
6. No ejecutar pruebas/migraciones contra producción por defecto ni versionar secretos, fotos reales, bases locales o archivos de entorno.
7. Documentar las verificaciones realizadas y actualizar limitaciones cuando se resuelvan.
8. Crear commits separados por mejoras significativas y verificadas, como pidió el propietario, para facilitar revisión y retroceso.
