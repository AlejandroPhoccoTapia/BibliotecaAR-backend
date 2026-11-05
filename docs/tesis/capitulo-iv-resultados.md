# Capítulo IV Análisis e interpretación de los resultados

> **Borrador sustentado en evidencia disponible al 5 de noviembre de 2026.** Las pruebas en un teléfono Android con ARCore y la comprobación del despliegue con Supabase todavía no se han ejecutado. Los casos pendientes se describen para completarlos antes de entregar la tesis. Las referencias IU corresponden al catálogo de interfaces y las RF a la especificación de requisitos del capítulo III.

## 4.1. Generalidades

Este capítulo verifica la correspondencia entre los dieciséis requisitos funcionales del sistema BibliotecaAR y los componentes que los implementan. La evaluación comprende el panel web de gestión docente, el servicio API desarrollado en Django y la aplicación móvil elaborada en Unity. Se distinguen tres niveles de evidencia: la presencia del mecanismo en el código y las interfaces, la ejecución de pruebas automáticas en un entorno local y la comprobación del recorrido completo en un teléfono conectado a los servicios desplegados. Una función implementada no se considera validada en el dispositivo únicamente porque existan sus scripts o porque haya pasado una prueba del servidor.

La verificación de cumplimiento localiza cada requisito en una interfaz o módulo concreto. Las pruebas automáticas comprueban comportamientos de la API y del panel web de forma reproducible; los casos manuales comprueban los aspectos que dependen de cámara, ARCore, seguimiento del marcador, audio y conexión con los servicios en la nube. Esta separación permite interpretar el alcance de los resultados sin atribuir al sistema mediciones que todavía no se han realizado.

Los resultados automáticos citados corresponden al código consultado el 5 de noviembre de 2026: backend `1c4d73a` y frontend `7651321`. La ejecución del backend utilizó `config.test_settings`, una base SQLite en memoria y archivos temporales locales. Por ello, no constituye una prueba de PostgreSQL ni de Supabase Storage. Las pruebas del panel ejecutaron Node.js sobre sus contratos de API y lógica de formularios; la compilación con Vite comprobó que la aplicación web puede generar un paquete de producción. No se dispone aún de una ejecución documentada en el celular ni de datos recogidos con estudiantes o docentes. En consecuencia, aquí no se calculan tasas de lectura correcta de QR, estabilidad del seguimiento, comprensión lectora, motivación o satisfacción.

## 4.2. Verificación de cumplimiento

La Tabla 4.1 relaciona cada requisito con el lugar donde se puede comprobar su implementación. **La tabla señala trazabilidad funcional, no un resultado experimental de «cumple» en el equipo final.** La comprobación de comportamiento se detalla en la sección 4.3.

| Requisito | Interfaz o módulo de cumplimiento |
| --- | --- |
| RF01. Registro y autenticación del docente | IU-01 Acceso y registro docente; IU-15 Acceso docente móvil; `TeacherRegisterView`, `TeacherLoginView` y sesión docente en `catalog/views.py`. |
| RF02. Gestión de cuentos digitales | IU-02 Biblioteca, IU-03 Formulario de libro e IU-04 Detalle de libro; modelo `Book` y API docente de libros. |
| RF03. Creación y gestión de escenas narrativas | IU-04 Detalle de libro e IU-05 Formulario de capítulo; modelo `Scene` y API docente de escenas. |
| RF04. Carga de recursos multimedia | IU-03, IU-05 e IU-07 para portada, audio, GLB y foto; validadores y campos de archivos en Django; vista previa GLB en IU-04. |
| RF05. Generación automática de códigos QR | IU-04 Detalle de libro; generación de identificador e imagen en `catalog/models.py`; PDF imprimible en `catalog/qr_pdf.py`. |
| RF06. Registro y gestión de estudiantes | IU-06 Lista, IU-07 Formulario e IU-08 Código generado; `StudentProfile` y API docente. |
| RF07. Asignación de cuentos a estudiantes | IU-07 selección de libros e IU-10 Biblioteca del estudiante; relación `assigned_books` y API estudiantil. |
| RF08. Reconocimiento facial del estudiante | IU-09 Acceso del estudiante; `catalog/face_recognition.py` y endpoint `POST /api/student/face-login/`. Es un mecanismo experimental. |
| RF09. Escaneo de códigos QR desde la aplicación móvil | IU-13 Escáner; `QRCodeScanner.cs` y biblioteca ZXing. |
| RF10. Consulta de escenas mediante API | Endpoint `GET /api/unity/scenes/<qr_code>/` en `catalog/views.py`; consumo desde `ARSceneController.cs` en IU-14. |
| RF11. Almacenamiento de datos en Supabase PostgreSQL | Configuración `DATABASE_URL` en `config/settings.py` y modelos de Django. Requiere verificar la conexión y persistencia en el despliegue real. |
| RF12. Almacenamiento de archivos en Supabase Storage | `config/storage_backends.py` y configuración `USE_SUPABASE_STORAGE` en `config/settings.py`. Requiere verificar carga y recuperación de archivos en el servicio real. |
| RF13. Visualización de contenido en realidad aumentada | IU-14 Escena AR; `QRTrackedImagePlacer.cs`, `ARSceneController.cs` y seguimiento de imágenes de AR Foundation/ARCore. |
| RF14. Reproducción de audio narrativo | IU-12 Lectura e IU-14 Escena AR; `ARSceneController.cs` y `AndroidNarrationVoice.cs`. |
| RF15. Carga y visualización de modelos 3D GLB | IU-04 vista previa web, IU-14 escena AR e IU-17 ajuste docente; carga mediante glTFast y parámetros físicos del capítulo. |
| RF16. Retorno al escáner QR desde la escena AR | IU-14 botón «Escanear otro QR»; `ARSceneController.BackToScanner()` carga IU-13. |

*Tabla 4.1. Relación entre requisitos funcionales e interfaces o módulos de BibliotecaAR. Elaboración propia.*

En RF11 y RF12 la implementación es configurable: el entorno local usa SQLite y archivos locales, mientras que el despliegue previsto usa PostgreSQL y Supabase Storage. Por eso, la presencia de la configuración no demuestra por sí sola el almacenamiento remoto. En RF08, la prueba automática de coincidencia visual no demuestra precisión biométrica para estudiantes reales.

## 4.3. Pruebas

### 4.3.1. Entorno y criterio de evaluación

Se aplicaron pruebas automáticas a las funciones que se pueden ejecutar sin un dispositivo y se definieron casos manuales para el recorrido completo. Una prueba se registra como **aprobada** solamente cuando el resultado obtenido coincide con el esperado y existe evidencia de la ejecución. Si todavía no se ejecutó, se registra como **pendiente**; no se asigna «Sí» ni un porcentaje estimado.

| Componente | Entorno usado | Comando o evidencia | Alcance |
| --- | --- | --- | --- |
| API Django | Pruebas de `catalog` con SQLite en memoria y almacenamiento local temporal, según `config.test_settings` | `python manage.py test catalog --settings=config.test_settings --verbosity 1` | Reglas del servidor, endpoints, validaciones, asignaciones, avance, QR y archivos simulados localmente. |
| Panel React | Node.js y pruebas del repositorio | `npm test` | Contratos de API, serialización de formularios, manejo de errores, búsqueda y orden de capítulos. |
| Compilación web | Vite en el repositorio frontend | `npm run build` | Generación del paquete web; no comprueba el uso de la interfaz por una persona. |
| Aplicación Android | Teléfono compatible con ARCore, cámara y acceso a la API | Casos CP-03 a CP-08 de la Tabla 4.3 | Pendiente de ejecutar y documentar. |
| Servicios en la nube | Backend desplegado, Supabase PostgreSQL y Storage configurados | Casos CP-02 y CP-07 de la Tabla 4.3 | Pendiente de ejecutar y documentar. |

*Tabla 4.2. Entornos y alcance de las pruebas. Elaboración propia.*

Para los casos móviles se debe registrar la marca y modelo del teléfono, versión de Android, versión de Google Play Services for AR, versión de la aplicación, URL del backend, fecha, condiciones de iluminación y ancho real del QR impreso. Estos datos permitirán repetir la prueba y explicar diferencias entre dispositivos o marcadores.

### 4.3.2. Resultados de las pruebas automáticas

El 5 de noviembre de 2026 se ejecutó la batería del backend: **51 pruebas, 51 aprobadas, 0 fallidas**. Entre las conductas cubiertas están registro docente, autorización, creación de libros y capítulos, generación de QR y PDF, validación de archivos GLB, asignación de libros, acceso estudiantil, persistencia lógica del avance y respuestas de la API. Se utilizó la configuración local de pruebas, por lo que el resultado no mide red, PostgreSQL ni Storage remotos. El directorio temporal se situó dentro del espacio de trabajo para permitir la escritura de archivos durante la ejecución.

La batería del frontend terminó con **7 pruebas, 7 aprobadas, 0 fallidas**. Se comprobó el contrato de peticiones, incluidos campos vacíos, listas de asignaciones, descarga PDF, errores de API, búsqueda y orden de capítulos. El comando `npm run build` finalizó correctamente. Vite emitió una advertencia de tamaño para el módulo de vista previa GLB; esa advertencia no impide compilar, pero justifica una revisión posterior del tiempo de carga de esa vista.

Estos resultados respaldan la lógica probada del servidor y del panel. No constituyen una medición del escaneo QR desde la cámara, la visualización AR, la calidad de la voz ni la facilidad de uso.

### 4.3.3. Casos de prueba de extremo a extremo

Los casos de la Tabla 4.3 se han definido conforme a los recorridos reales del sistema. **Su resultado observado sigue pendiente** hasta ejecutar cada caso y conservar capturas o registros. Se recomienda un libro de prueba con dos capítulos: uno con audio grabado y GLB animado; otro sin audio para comprobar la voz de Android. Ambos deben tener QR impresos al 100 % de escala, con la medida configurada en el capítulo. Debe existir además un libro en borrador para comprobar el control de publicación.

| Caso y requisitos | Precondición y procedimiento | Resultado esperado | Resultado observado |
| --- | --- | --- | --- |
| CP-01. Gestión docente (RF01 a RF05) | Sin sesión, registrar docente; crear libro y dos capítulos; adjuntar portada, audio y GLB; consultar el QR y descargar su PDF. | La cuenta accede al panel; los registros y archivos aparecen en IU-02 a IU-05; cada capítulo tiene QR único y el PDF muestra la medida física configurada. | Pendiente de ejecución manual. La API y la generación del PDF cuentan con pruebas automáticas parciales. |
| CP-02. Estudiante y continuidad (RF06 a RF08) | Crear un estudiante, asignarle un libro y obtener su código; iniciar sesión en el móvil; abrir y completar un capítulo; cerrar y volver a entrar. Probar el acceso facial por separado. | El libro aparece en «Mis libros», el progreso se recupera al reingresar y un código restablecido invalida el anterior. El rostro coincidente permite acceder; una persona no registrada no debe acceder. | Pendiente en móvil. Las reglas de asignación, progreso y código tienen pruebas de API; falta evaluar el acceso facial con personas y condiciones reales. |
| CP-03. Lectura de QR y consulta de contenido (RF09 y RF10) | Con la app instalada, escanear un QR publicado; repetir con QR inexistente, libro en borrador y conexión interrumpida. | El QR publicado abre su capítulo correcto. Los otros estados muestran un mensaje comprensible y una acción de recuperación cuando procede. | Pendiente de ejecución en teléfono. |
| CP-04. Seguimiento y colocación AR (RF13 y RF15) | Con el QR impreso a tamaño real, encuadrar la página; observar el modelo; alejar, acercar y recuperar el seguimiento; repetir con otro tamaño de marcador y otro GLB. | El modelo aparece sobre el QR, mantiene las dimensiones físicas configuradas, se oculta al perder seguimiento y vuelve al recuperarlo. | Pendiente de ejecución en teléfono con ARCore. |
| CP-05. Ajuste docente y animación (RF13 y RF15) | Acceder como docente móvil; escanear el capítulo; mover, girar, elevar y escalar el modelo con gestos; guardar, volver a escanear y tocar la vista para activar el clip elegido. | Los cambios se conservan en la escena; el tamaño del modelo responde a los centímetros guardados y se reproduce el clip configurado, si existe en el GLB. | Pendiente de ejecución en teléfono. |
| CP-06. Lectura y audio (RF14) | Abrir el capítulo con audio y otro sin audio; usar «Escuchar», «Pausar» y continuar; revisar texto largo, plegado de la tarjeta y orientación de pantalla. | El audio subido se reproduce; sin archivo se usa la voz española disponible en Android; los controles y el texto permanecen legibles y operables. | Pendiente de ejecución en teléfono. |
| CP-07. Persistencia y archivos en nube (RF11 y RF12) | Con Render y Supabase configurados, crear un libro y cargar archivos desde una sesión; abrirlos en otra sesión y en el móvil; reiniciar el servicio y volver a consultar. | Metadatos y progreso persisten en PostgreSQL; portada, QR, audio y GLB se recuperan desde Storage mediante las URLs de la API. | Pendiente de ejecución en el despliegue real. |
| CP-08. Navegación repetida (RF16) | En la escena AR, pulsar «Escanear otro QR» y leer el QR de otro capítulo. | La app vuelve a IU-13 y abre el nuevo capítulo sin reiniciarse ni conservar contenido del anterior. | Pendiente de ejecución en teléfono. |

*Tabla 4.3. Casos de prueba propuestos para la validación integral de BibliotecaAR. Elaboración propia.*

Para completar cada caso se debe añadir una ficha con fecha, ejecutor, dispositivo o navegador, pasos realizados, resultado esperado, resultado obtenido, estado y evidencia numerada. En CP-03 puede calcularse la proporción de QR leídos correctamente sobre intentos controlados; en CP-04, la proporción de sesiones en que el modelo aparece y recupera el seguimiento. Esos porcentajes solo deben incorporarse cuando exista un número registrado de intentos y un criterio de éxito definido. La evaluación de motivación o comprensión lectora exige, además, un instrumento y participantes; no se deduce de que la aplicación funcione técnicamente.

### 4.3.4. Interpretación de los resultados disponibles

Las pruebas locales muestran que las reglas verificadas de la API y del panel web funcionan en el entorno de ensayo y que el frontend compila. La trazabilidad de la Tabla 4.1 permite localizar los dieciséis requisitos, pero el cumplimiento integral de RF08, RF09 y RF11 a RF16 permanece sin evidencia de uso real. La siguiente etapa de evaluación debe ejecutar los casos pendientes sobre un teléfono compatible con ARCore y el despliegue previsto. Solo después podrá concluirse con fundamento sobre el comportamiento de la experiencia completa de narrativa aumentada y sobre la hipótesis de la investigación.
