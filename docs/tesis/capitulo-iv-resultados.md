# CAPÍTULO IV: ANÁLISIS E INTERPRETACIÓN DE LOS RESULTADOS

> Texto preparado el 5 de noviembre de 2026 para la tesis «Sistema de narrativa de cuentos virtuales empleando realidad aumentada». Su versión Word es `capitulo-iv-pruebas-completo.docx` y sustituye al borrador parcial `pruebas-ejecutadas-capitulo-iv.docx`, basado en una ejecución anterior. Los resultados locales de esta versión sí fueron ejecutados. Los resultados de implantación en celular y en Supabase permanecen sin registrar; deben completarse con observaciones propias antes de presentar el capítulo como validación integral.

## 4.1. Generalidades

Este capítulo verifica la implementación de los requisitos funcionales de BibliotecaAR y presenta las pruebas realizadas sobre el panel web y la API. Además, establece casos de implantación para comprobar el recorrido completo en el teléfono Android y en los servicios desplegados. Se distingue el resultado obtenido en una ejecución del comportamiento que aún está pendiente de observar; la existencia de una interfaz o de código fuente no se toma como prueba de funcionamiento en el entorno final.

## 4.2. Entorno y herramientas de prueba

Las pruebas locales se ejecutaron el 5 de noviembre de 2026 sobre los repositorios backend `07c4619` y frontend `0403e9d`. El código móvil revisado corresponde al commit `1ebc89b`; en este capítulo todavía no se le atribuyen resultados de escaneo o realidad aumentada. La Tabla 4.1 precisa el entorno que produjo los resultados. La configuración `config.test_settings` sustituye la base de datos y el almacenamiento remoto por recursos temporales locales, de modo que las pruebas automáticas no modifican datos de Supabase.

| Elemento | Configuración utilizada | Alcance de la comprobación |
| --- | --- | --- |
| Equipo de desarrollo | Windows; Python 3.12.14; Node.js 24.20.0; npm 11.19.0 | Ejecución local de las baterías y compilación web. |
| API | Django 6.0.7; `config.test_settings`; SQLite en memoria; archivos temporales locales | Reglas de negocio, validaciones, autenticación y respuestas HTTP. |
| Panel docente | React y Vite; pruebas con `node --test`; ESLint | Contratos de petición, transformación de formularios, lógica auxiliar, análisis estático y generación del paquete web. |
| Aplicación Android | Proyecto Unity 6000.3.19f1; Android con cámara y compatibilidad ARCore | Casos de implantación CP-02 a CP-06 y CP-08; resultados pendientes de registro. |
| Servicios desplegados | API en Render; PostgreSQL y Storage de Supabase según las variables de entorno | Persistencia e intercambio real de archivos: caso CP-07 pendiente. |

*Tabla 4.1. Entorno y alcance de las pruebas. Fuente: elaboración propia.*

Los comandos reproducibles fueron `python manage.py test catalog --settings=config.test_settings --verbosity 1` para Django, y `npm test`, `npm run lint` y `npm run build` para el panel. Se considera aprobado un caso automático cuando termina sin fallas y sus aserciones coinciden con el resultado esperado. En los casos de implantación se exige observar cada paso y conservar su evidencia; «no ejecutado» no equivale a «cumple» ni a «falla».

## 4.3. Verificación de cumplimiento funcional

La Tabla 4.2 relaciona los dieciséis requisitos del Capítulo III con la interfaz o el módulo que permite verificarlos. La última columna distingue la evidencia disponible. «Prueba local» se limita a las condiciones de la Tabla 4.1; «pendiente en dispositivo» o «pendiente en nube» indica que falta comprobar el recorrido instalado. Esta tabla sirve como lista de cotejo y guía de trazabilidad, sin atribuir resultados experimentales a funciones que todavía no se observaron.

| Requisito | Interfaz o módulo de cumplimiento | Evidencia disponible |
| --- | --- | --- |
| RF01. Registro y autenticación docente | IU-01; IU-15; vistas de registro, acceso y sesión en Django | Prueba local de API; acceso móvil pendiente. |
| RF02. Gestión de cuentos | IU-02 a IU-04; modelo `Book` y API docente | Prueba local de API; recorrido desplegado pendiente. |
| RF03. Gestión de escenas | IU-04 e IU-05; modelo `Scene` y API docente | Prueba local de API; recorrido desplegado pendiente. |
| RF04. Recursos multimedia | IU-03, IU-05 e IU-07; validadores y campos de archivos | Validación local; Storage remoto pendiente. |
| RF05. Generación de QR | IU-04; modelo de escena y `catalog/qr_pdf.py` | QR y PDF probados localmente; impresión física pendiente. |
| RF06. Gestión de estudiantes | IU-06 a IU-08; `StudentProfile` y API docente | Prueba local de API; acceso desde móvil pendiente. |
| RF07. Asignación de cuentos | IU-07 e IU-10; relación `assigned_books` y API estudiantil | Reglas locales probadas; presentación móvil pendiente. |
| RF08. Identificación facial | IU-09; `catalog/face_recognition.py` y API de acceso facial | Cotejo con imagen sintética probado; desempeño con personas pendiente. |
| RF09. Escaneo de QR | IU-13; `QRCodeScanner.cs` y ZXing | Pendiente de cámara en Android. |
| RF10. Consulta de escenas | `GET /api/unity/scenes/<qr_code>/`; `ARSceneController.cs` | Respuestas de API probadas localmente; consumo móvil pendiente. |
| RF11. Datos en PostgreSQL | `DATABASE_URL`, modelos y migraciones Django | Configuración identificada; persistencia remota pendiente. |
| RF12. Archivos en Storage | `config/storage_backends.py` y `USE_SUPABASE_STORAGE` | Configuración identificada; carga y descarga remota pendientes. |
| RF13. Visualización AR | IU-14; `QRTrackedImagePlacer.cs` y AR Foundation/ARCore | Pendiente de prueba con marcador físico. |
| RF14. Audio narrativo | IU-12 e IU-14; audio del capítulo y `AndroidNarrationVoice.cs` | Pendiente de escucha en Android. |
| RF15. Modelos GLB | IU-04, IU-14 e IU-17; validador, vista previa y glTFast | Archivo validado localmente; representación AR pendiente. |
| RF16. Retorno al escáner | IU-14; `ARSceneController.BackToScanner()` | Pendiente de navegación en Android. |

*Tabla 4.2. Lista de cotejo y trazabilidad de los requisitos funcionales. Fuente: elaboración propia.*

La lista permite ubicar los dieciséis requisitos, pero su cobertura documental no significa que los dieciséis estén validados en el teléfono. En particular, RF08 solo cuenta con un cotejo sintético: no se ha medido tasa de falsos aceptados o rechazados. RF11 y RF12 necesitan probarse con las credenciales y servicios reales del despliegue.

## 4.4. Pruebas funcionales automatizadas

### 4.4.1. Objetivo y método

El objetivo fue comprobar, de manera repetible, las reglas del servidor y las transformaciones del panel que pueden evaluarse sin cámara. La batería Django crea una base de datos de prueba en memoria, solicita endpoints y contrasta códigos de respuesta y datos devueltos. La batería del frontend ejecuta casos de contrato y lógica en Node.js; ESLint detecta problemas estáticos y Vite comprueba que se genera el paquete distribuible. La aprobación de estas baterías no mide tiempos de respuesta por internet ni la experiencia de uso de una persona.

### 4.4.2. Casos y resultados obtenidos

| Caso | Comprobación principal | Resultado obtenido | Estado |
| --- | --- | --- | --- |
| PA-01. API y reglas de negocio | Registro docente, permisos, libros, escenas, estudiantes, asignaciones, progreso, QR/PDF y consulta de capítulos; validación de archivos y ajustes AR | 52 pruebas ejecutadas; 52 aprobadas; 0 fallidas. | Aprobado en entorno local. |
| PA-02. Contrato y lógica del panel | Peticiones con CSRF, descarga del PDF, datos vacíos, asignaciones múltiples, errores de API, búsqueda y orden de capítulos | 7 pruebas ejecutadas; 7 aprobadas; 0 fallidas. | Aprobado en entorno local. |
| PA-03. Análisis estático | Reglas ESLint del código JavaScript y JSX | Proceso finalizado sin errores. | Aprobado. |
| PA-04. Compilación web | Generación del paquete de producción con Vite | Compilación finalizada; se generaron los archivos de `dist`. | Aprobado con advertencia de tamaño. |

*Tabla 4.3. Resultados de las pruebas locales ejecutadas el 5 de noviembre de 2026. Fuente: elaboración propia a partir de la salida de los comandos de prueba.*

En conjunto, **59 de 59 pruebas automatizadas terminaron correctamente** en esta versión: 52 del backend y 7 del frontend. La compilación web mostró una advertencia porque el módulo diferido de vista previa GLB supera 500 kB tras minificación. La advertencia no detuvo la compilación; tampoco permite concluir cuánto demora esa vista en una conexión real. Las 52 pruebas Django utilizaron SQLite y archivos temporales, por lo que no comprueban PostgreSQL ni Supabase Storage. La prueba facial incluida usa datos sintéticos y no demuestra precisión biométrica con estudiantes.

## 4.5. Pruebas de implantación

### 4.5.1. Objetivo y método

Estas pruebas buscan comprobar el recorrido del sistema tal como lo usarían el docente y el estudiante: panel web, API desplegada, almacenamiento remoto, aplicación Android, QR impreso y página física. Se prepara un libro de prueba publicado con dos capítulos y otro libro en borrador. El primer capítulo debe incluir un GLB con una animación y audio grabado; el segundo, un GLB diferente y texto sin archivo de audio, para observar la voz del dispositivo. Los QR se imprimen al 100 % del PDF y se mide su ancho real antes de escanearlos.

Cada caso se ejecuta paso por paso, anotando fecha, responsable, versiones, dispositivo, red, ancho del QR, condición de iluminación y evidencia. La columna «Resultado obtenido» se completa después de observar el sistema. El paso se marca «Sí» únicamente si lo obtenido coincide con lo esperado; si difiere, se consigna «No» y la incidencia; si aún no se ejecutó, se mantiene «NE». Se usan perfiles y contenidos de prueba y se ocultan rostros, contraseñas y códigos privados en las capturas.

### 4.5.2. Casos de prueba

| Caso | Nombre | Requisitos | Qué comprueba |
| --- | --- | --- | --- |
| CP-01 | Gestión docente y publicación | RF01–RF05 | Cuenta, libro, capítulos, archivos y QR/PDF desde el panel desplegado. |
| CP-02 | Estudiante, asignaciones y avance | RF06–RF08 | Perfil, acceso, biblioteca asignada, continuidad y acceso facial exploratorio. |
| CP-03 | Escaneo y consulta | RF09–RF10 | Lectura de QR válido, borrador, inexistente y pérdida de conexión. |
| CP-04 | Colocación y seguimiento AR | RF13, RF15 | Posición, tamaño y recuperación del modelo sobre el marcador. |
| CP-05 | Ajuste docente y animación | RF13, RF15 | Gestos, guardado de medidas y activación del clip al tocar la vista. |
| CP-06 | Lectura y narración | RF14 | Texto legible, audio grabado, voz de Android y controles. |
| CP-07 | Persistencia en la nube | RF11–RF12 | Datos y archivos recuperables entre sesiones y tras reiniciar el servicio. |
| CP-08 | Navegación y recuperación | RF09, RF10, RF16 | Retorno al escáner, segundo QR, permisos y mensajes ante fallos. |

*Tabla 4.4. Casos de prueba de implantación de BibliotecaAR. Fuente: elaboración propia.*

### 4.5.3. Desarrollo de los casos

**CP-01. Gestión docente y publicación (RF01–RF05).** Precondición: API desplegada operativa; navegador sin sesión; archivos de prueba válidos; docente de prueba disponible o correo y usuario nuevos. Evidencia por incorporar: capturas IU-01 a IU-05 y PDF del QR.

| Paso | Acción | Resultado esperado | Resultado obtenido / Cumple |
| --- | --- | --- | --- |
| 1 | Registrar un docente e iniciar sesión en IU-01. | La cuenta docente accede al catálogo y conserva la sesión al recargar. | No ejecutado / NE. |
| 2 | Crear un libro con portada en IU-03. | El libro aparece en IU-02 y puede abrirse en IU-04. | No ejecutado / NE. |
| 3 | Crear dos capítulos con texto, audio y modelos GLB en IU-05. | Se guardan ambos capítulos en orden y los archivos correctos se muestran en el detalle. | No ejecutado / NE. |
| 4 | Publicar el libro, descargar los QR, imprimir el PDF al 100 % y medirlo. | Cada capítulo tiene QR distinto; el ancho impreso y la referencia de 5 cm corresponden a lo configurado, dentro de la precisión de la regla utilizada. | No ejecutado / NE. |

*Tabla 4.5. Caso CP-01. Fuente: elaboración propia.*

**CP-02. Estudiante, asignaciones y avance (RF06–RF08).** Precondición: libro publicado de CP-01, estudiante ficticio y teléfono con la aplicación instalada. El reconocimiento facial se realiza solo con una persona voluntaria y su consentimiento, y se informa aparte del acceso por código. Evidencia por incorporar: IU-06 a IU-12 y respuestas de la API sin datos sensibles.

| Paso | Acción | Resultado esperado | Resultado obtenido / Cumple |
| --- | --- | --- | --- |
| 1 | Registrar el estudiante en IU-07 y asignarle un libro. | El perfil aparece en IU-06 y el libro queda vinculado. | No ejecutado / NE. |
| 2 | Usar el código mostrado en IU-08 para entrar desde IU-09. | Se abre «Mis libros» en IU-10 con el libro publicado asignado. | No ejecutado / NE. |
| 3 | Abrir el libro y un capítulo, marcarlo como leído y volver a entrar. | El avance se conserva y permite retomar el capítulo correspondiente. | No ejecutado / NE. |
| 4 | Restablecer el código y probar el anterior y el nuevo. | El código antiguo deja de autenticar; el nuevo permite entrar. | No ejecutado / NE. |
| 5 | Probar acceso facial con rostro registrado y no registrado, con consentimiento. | El rostro registrado puede identificarse y el no registrado no debe obtener acceso; se anotan los errores observados. | No ejecutado / NE. |

*Tabla 4.6. Caso CP-02. Fuente: elaboración propia.*

**CP-03. Escaneo y consulta de escenas (RF09–RF10).** Precondición: QR publicados impresos, un QR de libro en borrador y teléfono con permiso de cámara. Evidencia por incorporar: IU-13, mensaje de carga, IU-14 y respuestas de error.

| Paso | Acción | Resultado esperado | Resultado obtenido / Cumple |
| --- | --- | --- | --- |
| 1 | Enfocar un QR publicado desde IU-13. | Se reconoce el código y se muestra que el capítulo se está cargando. | No ejecutado / NE. |
| 2 | Esperar la respuesta de la API. | Se abre el capítulo correcto con su título y narración. | No ejecutado / NE. |
| 3 | Escanear un QR inexistente y uno de un libro en borrador. | La app informa que no hay contenido disponible sin mostrar un capítulo incorrecto. | No ejecutado / NE. |
| 4 | Cortar la conexión y volver a escanear; después restablecerla y reintentar. | Se informa el fallo de conexión y el reintento permite cargar cuando vuelve la red. | No ejecutado / NE. |

*Tabla 4.7. Caso CP-03. Fuente: elaboración propia.*

**CP-04. Colocación y seguimiento AR (RF13 y RF15).** Precondición: dispositivo compatible con ARCore, GLB válido, página con QR plano y ancho medido. Realizar la secuencia con dos GLB de dimensiones originales diferentes. Evidencia por incorporar: captura de IU-14 con modelo visible y registro del seguimiento.

| Paso | Acción | Resultado esperado | Resultado obtenido / Cumple |
| --- | --- | --- | --- |
| 1 | Enfocar el QR y mover lentamente el teléfono sobre la página. | El modelo aparece sobre el marcador al establecerse el seguimiento. | No ejecutado / NE. |
| 2 | Comparar visualmente la colocación y medir la dimensión mayor del objeto representado. | El objeto conserva la medida física configurada para el capítulo, sin depender de la escala original del GLB. | No ejecutado / NE. |
| 3 | Alejar el marcador de la cámara y volver a enfocarlo. | La app indica la pérdida de seguimiento y recupera la visualización al reenfocar. | No ejecutado / NE. |
| 4 | Repetir con un QR y GLB distintos. | Cada capítulo carga su propio objeto y sus parámetros sin reutilizar el anterior. | No ejecutado / NE. |

*Tabla 4.8. Caso CP-04. Fuente: elaboración propia.*

**CP-05. Ajuste docente y animación (RF13 y RF15).** Precondición: docente autenticado en IU-15, capítulo con GLB animado y QR impreso. Evidencia por incorporar: IU-16, IU-17, valores guardados y vista AR posterior.

| Paso | Acción | Resultado esperado | Resultado obtenido / Cumple |
| --- | --- | --- | --- |
| 1 | Desde IU-16 escanear el QR y abrir el ajuste en IU-17. | Aparecen el modelo y las instrucciones de gestos sin impedir ver la página. | No ejecutado / NE. |
| 2 | Arrastrar, pellizcar, girar y elevar el modelo según las indicaciones. | Cambian posición, tamaño, giro o altura conforme al gesto realizado. | No ejecutado / NE. |
| 3 | Guardar, volver a escanear el mismo QR y comprobar la colocación. | Se recuperan los valores guardados para ese capítulo. | No ejecutado / NE. |
| 4 | Tocar la vista fuera de los controles con el clip elegido en el panel. | Se reproduce la animación configurada sin desplazar el objeto; si el clip no existe, se informa. | No ejecutado / NE. |

*Tabla 4.9. Caso CP-05. Fuente: elaboración propia.*

**CP-06. Lectura y narración (RF14).** Precondición: un capítulo con audio subido y otro con texto pero sin audio; salida de sonido disponible. Evidencia por incorporar: IU-12 o IU-14 y registro de escucha.

| Paso | Acción | Resultado esperado | Resultado obtenido / Cumple |
| --- | --- | --- | --- |
| 1 | Abrir un texto narrativo largo y desplazar la lectura. | El texto se lee completo, con contraste suficiente y sin quedar tapado por bordes o controles. | No ejecutado / NE. |
| 2 | Reproducir y pausar el capítulo con audio grabado. | Se oye el archivo correcto y los controles reflejan el estado. | No ejecutado / NE. |
| 3 | Abrir el capítulo sin archivo de audio y pulsar «Escuchar». | Se utiliza la voz española disponible en Android o se explica cómo habilitarla. | No ejecutado / NE. |
| 4 | Cerrar la lectura y volver a abrirla. | No queda audio de la escena anterior reproduciéndose; la nueva reproducción responde a los controles. | No ejecutado / NE. |

*Tabla 4.10. Caso CP-06. Fuente: elaboración propia.*

**CP-07. Persistencia y recursos en la nube (RF11–RF12).** Precondición: Render conectado a PostgreSQL de Supabase, Storage habilitado, migraciones aplicadas y dos sesiones de prueba. Evidencia por incorporar: respuestas HTTP, pantallas antes y después del reinicio, y URLs de recursos sin credenciales.

| Paso | Acción | Resultado esperado | Resultado obtenido / Cumple |
| --- | --- | --- | --- |
| 1 | Crear un libro y capítulo desde la primera sesión. | Los registros se guardan y la API devuelve sus identificadores. | No ejecutado / NE. |
| 2 | Subir portada, audio y GLB y consultarlos desde otra sesión autorizada. | Cada URL recupera el archivo correcto desde el almacenamiento configurado. | No ejecutado / NE. |
| 3 | Registrar un estudiante y su avance; cerrar ambas sesiones y abrir una nueva. | Libros, capítulos, asignaciones y avance permanecen disponibles. | No ejecutado / NE. |
| 4 | Reiniciar el servicio backend y repetir las consultas. | Los datos y archivos continúan accesibles; no dependen del disco temporal de Render. | No ejecutado / NE. |

*Tabla 4.11. Caso CP-07. Fuente: elaboración propia.*

**CP-08. Navegación y recuperación (RF09, RF10 y RF16).** Precondición: dos QR publicados y aplicación Android instalada. Evidencia por incorporar: IU-13 e IU-14, mensajes de permiso y secuencia de navegación.

| Paso | Acción | Resultado esperado | Resultado obtenido / Cumple |
| --- | --- | --- | --- |
| 1 | En IU-14 pulsar «Escanear otro QR». | La app vuelve a IU-13 sin reiniciarse. | No ejecutado / NE. |
| 2 | Escanear el QR de otro capítulo. | Se carga el nuevo capítulo sin conservar título, narración, audio o modelo del anterior. | No ejecutado / NE. |
| 3 | Denegar el permiso de cámara y abrir el escáner. | Aparece un mensaje comprensible con una acción para volver a intentar o habilitar el permiso. | No ejecutado / NE. |
| 4 | Recuperar el permiso y reabrir el escáner. | La cámara vuelve a funcionar y se puede leer un QR. | No ejecutado / NE. |

*Tabla 4.12. Caso CP-08. Fuente: elaboración propia.*

## 4.6. Indicadores de desempeño

Se informan por separado los resultados medidos y los indicadores que aún requieren pruebas de campo. No se fija una meta porcentual que no figure en el diseño de la investigación. Para las mediciones pendientes se deben registrar tanto el numerador como el denominador, además de las condiciones de prueba; un porcentaje aislado no permite valorar la repetibilidad.

| Indicador | Cálculo o método | Objetivo relacionado | Resultado al 5 de noviembre de 2026 |
| --- | --- | --- | --- |
| Pruebas automáticas aprobadas | Pruebas aprobadas / pruebas ejecutadas | OE3, OE4 y OE8 | 59/59 en entorno local: 52 backend y 7 frontend. |
| Lectura correcta de QR | Intentos que abren el capítulo esperado / intentos con QR válido | OE5, OE6 y OE8 | Pendiente de registrar con la cámara. |
| Tiempo de carga de escena | Segundos desde lectura del QR hasta texto y escena disponibles; informar mediana y rango | OE6 y OE8 | Pendiente de medición en teléfono y red real. |
| Recursos remotos disponibles | Descargas correctas / solicitudes de portada, audio, QR y GLB | OE4, OE7 y OE8 | Pendiente de ejecución con Supabase Storage. |
| Seguimiento AR estable | Tiempo con modelo alineado y visible / tiempo total de observación, indicando distancia y luz | OE7 y OE8 | Pendiente de medición con marcador físico. |
| Recuperación del seguimiento | Reenfoques que restauran el modelo / pérdidas de seguimiento provocadas | OE7 y OE8 | Pendiente de ejecución en Android. |
| Exactitud del ancho impreso | Diferencia absoluta, en milímetros, entre ancho configurado y medido | OE5 y OE7 | Pendiente de imprimir y medir el PDF. |
| Acceso facial exploratorio | Aciertos y errores de aceptación/rechazo con participantes consentidos, indicando tamaño de muestra | OE5 y OE8 | Sin muestra humana; no se informa precisión. |
| Comprensión, motivación y satisfacción | Instrumento y participantes definidos previamente, con resultados por persona | Calidad de la experiencia narrativa | No evaluadas en estas pruebas técnicas. |

*Tabla 4.13. Indicadores y estado de medición. Fuente: elaboración propia.*

El cociente 59/59 describe únicamente la batería automática ejecutada: no representa una tasa de éxito general del sistema. Para la lectura QR, las pruebas deben repetirse con diversos capítulos y condiciones de iluminación registradas. Para el seguimiento AR, se debe definir una duración fija por ensayo. La comprensión del cuento y la motivación son resultados educativos o de percepción; requieren un diseño con estudiantes e instrumentos apropiados, por lo que no pueden inferirse del funcionamiento técnico.

## 4.7. Contrastación de la hipótesis e interpretación

La hipótesis del Capítulo I plantea que, empleando realidad aumentada, es posible implementar un sistema de narrativa de cuentos virtuales. La prueba no exige una comparación estadística con un sistema anterior, porque la hipótesis está formulada como factibilidad de implementación. Para contrastarla técnicamente se necesita observar la cadena completa: creación y publicación del capítulo, consulta mediante QR en Android, recuperación de sus recursos y presentación de texto, audio y modelo 3D sobre la página física.

| Aspecto de la hipótesis | Evidencia obtenida | Evidencia que falta | Interpretación |
| --- | --- | --- | --- |
| Gestión y entrega de contenido | 52 pruebas del backend y 7 del frontend aprobadas; compilación web correcta. | CP-01, CP-02 y CP-07 en los servicios desplegados. | Existe soporte local para el flujo de gestión y consulta; falta comprobar la implantación. |
| Acceso mediante QR e identificación | Generación de QR y respuestas de API probadas localmente; cotejo facial sintético. | CP-02 y CP-03 con cámara y participantes consentidos. | No hay tasa de lectura ni precisión facial medida. |
| Presentación aumentada de la narrativa | Componentes Unity implementados para texto, audio, GLB y seguimiento. | CP-04 a CP-06 y CP-08 en Android con página y QR reales. | La experiencia AR aún no tiene evidencia de ejecución en este capítulo. |

*Tabla 4.14. Estado de la contrastación de la hipótesis. Fuente: elaboración propia.*

Los resultados disponibles respaldan el funcionamiento de la lógica local del panel y de la API, y aportan evidencia parcial a OE3, OE4, OE5 y OE8. Todavía no permiten declarar cumplido experimentalmente el objetivo general ni aceptar de forma definitiva la hipótesis, porque faltan los casos de implantación móvil y de persistencia remota. Una vez registrados los resultados obtenidos de CP-01 a CP-08, esta conclusión debe actualizarse con las incidencias y medidas reales, sin reemplazar un ensayo faltante por la existencia de código o por una captura de pantalla aislada.
