# Especificación de requisitos funcionales de BibliotecaAR

Fichas RF01 a RF16, versión 1.0, elaboradas el 04/11/2026. Se distinguen las funciones disponibles de las condiciones de despliegue: el acceso facial es experimental; PostgreSQL y Supabase Storage requieren configuración. Los códigos IU corresponden al [catálogo de interfaces](catalogo-interfaces.md).

## RF01 Registro y autenticación del docente

| Campo | Especificación |
| --- | --- |
| Código | RF01 |
| Nombre del requisito | Registro y autenticación del docente |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** El sistema permite crear una cuenta docente con usuario y contraseña, iniciar y cerrar sesión en el panel web y acceder a la vista docente de la aplicación móvil. Las cuentas creadas por el registro público reciben el rol docente.

**Precondiciones**

- Hay conexión con la API y la base de datos.
- Para iniciar sesión, existe una cuenta docente activa.

**Acciones desarrolladas por el sistema**

- Presenta el formulario de registro o acceso (IU-01).
- Valida usuario único y contraseña según las reglas de Django; crea la cuenta con permiso docente.
- Autentica las credenciales y habilita las funciones del panel; para la vista móvil entrega un token temporal.

**Acciones desarrolladas por el usuario**

- Ingresa nombre de usuario, contraseña y, si registra la cuenta, nombre y apellidos opcionales.
- Envía el formulario o inicia sesión; puede cerrar la sesión al terminar.

**Poscondiciones.** La cuenta queda registrada o el docente accede a las funciones autorizadas; al cerrar sesión se revoca la sesión correspondiente.

**Flujo alternativo.** Si el usuario ya existe, la contraseña no cumple las reglas, las credenciales son incorrectas o la API no responde, se muestra un error y no se concede acceso.

## RF02 Gestión de cuentos digitales

| Campo | Especificación |
| --- | --- |
| Código | RF02 |
| Nombre del requisito | Gestión de cuentos digitales |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** El docente administra el catálogo compartido de cuentos o libros digitales: registra título, descripción y portada, edita o elimina libros y decide si cada uno está publicado o en borrador.

**Precondiciones**

- El docente inició sesión y tiene permisos de administración.

**Acciones desarrolladas por el sistema**

- Muestra la biblioteca y el formulario de libro (IU-02 e IU-03).
- Valida los datos y guarda las altas, modificaciones, eliminaciones y cambios de publicación.
- Entrega al estudiante solo libros publicados en las consultas públicas.

**Acciones desarrolladas por el usuario**

- Crea o selecciona un libro y completa o modifica sus datos.
- Guarda, publica, devuelve a borrador o elimina el libro cuando corresponda.

**Poscondiciones.** El catálogo refleja el cambio; un libro en borrador queda fuera de la biblioteca pública del estudiante.

**Flujo alternativo.** Si faltan datos obligatorios, la portada no es aceptada o falla la conexión, el cambio no se confirma y se informa el problema.

## RF03 Creación y gestión de escenas narrativas

| Campo | Especificación |
| --- | --- |
| Código | RF03 |
| Nombre del requisito | Creación y gestión de escenas narrativas |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** El docente crea, ordena, consulta, edita y elimina capítulos narrativos asociados a un libro. Cada capítulo almacena texto, posición dentro del libro y parámetros de colocación del modelo en AR.

**Precondiciones**

- El docente está autenticado y existe el libro al que pertenecerá el capítulo.

**Acciones desarrolladas por el sistema**

- Muestra el detalle del libro y el formulario del capítulo (IU-04 e IU-05).
- Exige un orden positivo y el texto narrativo; guarda los datos del capítulo.
- Asocia automáticamente un identificador QR al capítulo nuevo.

**Acciones desarrolladas por el usuario**

- Abre el libro, añade o edita un capítulo y escribe su texto y orden.
- Guarda los cambios o elimina el capítulo seleccionado.

**Poscondiciones.** El capítulo queda vinculado al libro y aparece en el orden definido en las consultas correspondientes.

**Flujo alternativo.** Si el libro no existe, faltan datos obligatorios o la API rechaza la solicitud, se conserva el estado anterior y se muestra el error.

## RF04 Carga de recursos multimedia

| Campo | Especificación |
| --- | --- |
| Código | RF04 |
| Nombre del requisito | Carga de recursos multimedia |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** El docente puede adjuntar una portada al libro, una foto al perfil del estudiante y audio o un modelo GLB al capítulo. El panel permite revisar los recursos disponibles antes de utilizarlos.

**Precondiciones**

- El docente está autenticado y dispone de un libro, estudiante o capítulo donde asociar el archivo.
- El archivo cumple los formatos y límites admitidos por la API.

**Acciones desarrolladas por el sistema**

- Recibe el archivo y valida tamaño y tipo; para GLB comprueba además la cabecera glTF 2.0.
- Guarda la referencia del recurso y devuelve su URL cuando existe.
- Permite reproducir audio y previsualizar el GLB desde el panel web.

**Acciones desarrolladas por el usuario**

- Selecciona el recurso en el formulario correspondiente y confirma el guardado.
- Revisa la vista previa o retira el modelo si ya no corresponde al capítulo.

**Poscondiciones.** El recurso aceptado queda asociado al registro y disponible mediante la API.

**Flujo alternativo.** Un archivo excesivo, un formato no admitido, un GLB incompleto o un fallo de almacenamiento produce un mensaje de error y evita usar ese recurso.

## RF05 Generación automática de códigos QR

| Campo | Especificación |
| --- | --- |
| Código | RF05 |
| Nombre del requisito | Generación automática de códigos QR |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** Al crear un capítulo, el sistema genera un identificador único y una imagen QR. El docente puede consultar el código y descargar una hoja PDF para imprimirlo con el ancho físico configurado.

**Precondiciones**

- Existe un libro y el docente registra o consulta un capítulo.
- Para descargar el PDF, el ancho del marcador está entre 2 y 30 cm.

**Acciones desarrolladas por el sistema**

- Genera y guarda el identificador y la imagen QR al registrar el capítulo.
- Muestra el QR en el detalle y produce un PDF con el QR completo a la medida guardada y una regla de comprobación de 5 cm.

**Acciones desarrolladas por el usuario**

- Crea el capítulo y abre su tarjeta QR en IU-04.
- Descarga el PDF e imprime al 100 % cuando vaya a usar el marcador físico.

**Poscondiciones.** El capítulo tiene un QR consultable y un PDF imprimible para el seguimiento AR.

**Flujo alternativo.** Si la generación o el almacenamiento falla, no se confirma el recurso; si la medida es inválida, el PDF se rechaza hasta corregirla.

## RF06 Registro y gestión de estudiantes

| Campo | Especificación |
| --- | --- |
| Código | RF06 |
| Nombre del requisito | Registro y gestión de estudiantes |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** El docente registra y administra perfiles de estudiantes con nombre, aula, fotografía opcional y estado activo. Al crear un perfil se genera un código de acceso personal que puede restablecerse.

**Precondiciones**

- El docente inició sesión en el panel.
- Para el acceso facial experimental se dispone de una foto de referencia válida.

**Acciones desarrolladas por el sistema**

- Muestra la lista y el formulario de estudiantes (IU-06 e IU-07).
- Guarda el perfil y genera un código de acceso; muestra el código nuevo una sola vez (IU-08) y conserva una representación verificable para autenticarlo.
- Al desactivar un perfil, invalida sus sesiones existentes.

**Acciones desarrolladas por el usuario**

- Completa o edita los datos del estudiante.
- Entrega el código generado al estudiante y lo restablece si se extravía.

**Poscondiciones.** El perfil queda disponible para acceder a la app mientras esté activo; el código anterior deja de funcionar al restablecerlo.

**Flujo alternativo.** Si faltan datos válidos, la fotografía no se puede procesar o falla la API, el sistema informa la causa y no completa la operación.

## RF07 Asignación de cuentos a estudiantes

| Campo | Especificación |
| --- | --- |
| Código | RF07 |
| Nombre del requisito | Asignación de cuentos a estudiantes |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** El docente vincula uno o varios cuentos a un estudiante. Los libros asignados y publicados aparecen en «Mis libros» dentro de la aplicación móvil. La asignación organiza la lectura, pero no impide consultar otros libros publicados mediante su QR.

**Precondiciones**

- Existe un perfil estudiantil y al menos un libro en el catálogo.
- El docente tiene sesión activa para modificar la asignación.

**Acciones desarrolladas por el sistema**

- Muestra los libros elegibles en el formulario del estudiante (IU-07).
- Guarda la relación entre el estudiante y los libros seleccionados.
- Devuelve los libros asignados publicados en la biblioteca móvil (IU-10).

**Acciones desarrolladas por el usuario**

- Selecciona o quita libros en el perfil y guarda.
- El estudiante abre «Mis libros» después de autenticarse.

**Poscondiciones.** La lista asignada del estudiante refleja los libros publicados vinculados a su perfil.

**Flujo alternativo.** Un libro en borrador puede seguir asignado, pero no se muestra al estudiante hasta publicarlo; si se elimina el libro, desaparece de la asignación.

## RF08 Reconocimiento facial del estudiante

| Campo | Especificación |
| --- | --- |
| Código | RF08 |
| Nombre del requisito | Reconocimiento facial del estudiante |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** La aplicación ofrece un acceso facial experimental: compara la foto capturada con firmas visuales calculadas a partir de las fotos registradas de estudiantes activos. Este mecanismo no constituye una verificación biométrica robusta para producción; el código personal permanece como alternativa.

**Precondiciones**

- El estudiante tiene un perfil activo con fotografía de referencia procesada.
- La cámara está disponible y la API puede recibir la imagen.

**Acciones desarrolladas por el sistema**

- Captura o recibe la imagen y calcula una firma de textura facial.
- Compara la firma con las registradas y, si una distancia cumple el umbral, emite una sesión de estudiante.

**Acciones desarrolladas por el usuario**

- Elige acceso por rostro en IU-09 y coloca su cara ante la cámara.
- Si el acceso falla, usa su código personal.

**Poscondiciones.** Cuando existe coincidencia aceptada, el estudiante accede a su biblioteca con una sesión temporal.

**Flujo alternativo.** Si no hay coincidencia, la imagen es inválida, falta permiso de cámara o falla la red, se informa el problema y se mantiene disponible el acceso por código.

## RF09 Escaneo de códigos QR desde la aplicación móvil

| Campo | Especificación |
| --- | --- |
| Código | RF09 |
| Nombre del requisito | Escaneo de códigos QR desde la aplicación móvil |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** El estudiante o docente utiliza la cámara Android para leer el QR impreso de un capítulo y abrir su experiencia de realidad aumentada.

**Precondiciones**

- La app está instalada, la cámara funciona y dispone de permiso.
- Hay un QR de capítulo legible frente al dispositivo.

**Acciones desarrolladas por el sistema**

- Muestra el visor y las indicaciones de escaneo (IU-13).
- Decodifica el contenido con ZXing, conserva temporalmente el identificador y abre la escena AR (IU-14).

**Acciones desarrolladas por el usuario**

- Elige «Escanear QR» y centra el código dentro del visor.
- Mantiene el teléfono estable hasta recibir confirmación.

**Poscondiciones.** El identificador leído queda disponible para solicitar el capítulo a la API.

**Flujo alternativo.** Si no hay permiso, la cámara falla o el código no se lee, la app muestra instrucciones y permite reintentar; un QR desconocido se informa al consultar la API.

## RF10 Consulta de escenas mediante API

| Campo | Especificación |
| --- | --- |
| Código | RF10 |
| Nombre del requisito | Consulta de escenas mediante API |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** La app móvil consulta a Django por el identificador del QR. Para lectura ordinaria, la API devuelve solo capítulos de libros publicados con texto, URLs de recursos y medidas AR; la vista docente autenticada puede consultar también borradores.

**Precondiciones**

- Se obtuvo un identificador QR.
- La API está disponible por red.

**Acciones desarrolladas por el sistema**

- Busca el capítulo por código y comprueba su estado de publicación.
- Devuelve los datos de narración, audio, GLB, imagen QR y colocación física en formato JSON.
- Entrega un error cuando el código no existe o el libro no está publicado.

**Acciones desarrolladas por el usuario**

- Escanea el QR y espera la carga del capítulo.
- El docente puede usar su sesión móvil para previsualizar un borrador.

**Poscondiciones.** La app dispone de los datos necesarios para la lectura y la preparación de AR.

**Flujo alternativo.** Sin conexión, ante una respuesta incompleta o con un QR no publicado, se explica el fallo y se ofrece reintentar o volver al escáner.

## RF11 Almacenamiento de datos en Supabase PostgreSQL

| Campo | Especificación |
| --- | --- |
| Código | RF11 |
| Nombre del requisito | Almacenamiento de datos en Supabase PostgreSQL |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** En el despliegue configurado con DATABASE_URL, Django persiste docentes, libros, capítulos, estudiantes, asignaciones, sesiones y progreso en PostgreSQL de Supabase. En desarrollo local, la configuración permite SQLite.

**Precondiciones**

- La instancia de PostgreSQL existe y DATABASE_URL apunta al proyecto correcto.
- El backend puede establecer una conexión segura y tiene migraciones aplicadas.

**Acciones desarrolladas por el sistema**

- Abre conexiones a la base configurada mediante Django.
- Guarda y consulta los registros de negocio según las operaciones de la API.
- Conserva las relaciones entre libros, capítulos, estudiantes y avance.

**Acciones desarrolladas por el usuario**

- El docente y el estudiante realizan las operaciones desde sus interfaces; no se conectan directamente a PostgreSQL.

**Poscondiciones.** Los cambios confirmados quedan persistidos y pueden recuperarse desde otra sesión autorizada.

**Flujo alternativo.** Si DATABASE_URL falta se usa SQLite local; si la conexión a PostgreSQL falla durante el despliegue o uso, la operación dependiente no se completa y requiere corregir la configuración o el servicio.

## RF12 Almacenamiento de archivos en Supabase Storage

| Campo | Especificación |
| --- | --- |
| Código | RF12 |
| Nombre del requisito | Almacenamiento de archivos en Supabase Storage |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** Cuando está habilitado y configurado USE_SUPABASE_STORAGE, Django guarda portadas, fotografías, audio, modelos GLB e imágenes QR en Supabase Storage mediante su interfaz compatible con S3. En desarrollo puede usar archivos locales.

**Precondiciones**

- Existe un bucket accesible y están configuradas las credenciales y el endpoint de Storage.
- El archivo ha superado las validaciones de la API.

**Acciones desarrolladas por el sistema**

- Envía el archivo al almacenamiento configurado y asocia su ruta al registro.
- Construye la URL del recurso para el panel o la app cuando corresponde.
- Limpia archivos reemplazados o eliminados después de confirmar los cambios de datos.

**Acciones desarrolladas por el usuario**

- El docente sube, reemplaza o retira archivos desde el panel web.

**Poscondiciones.** Los recursos guardados se pueden recuperar mediante la URL entregada por la API.

**Flujo alternativo.** Si faltan credenciales o Storage falla, la carga o consulta del archivo puede fallar; el backend debe informar el error. Con Storage deshabilitado se utiliza el sistema de archivos local.

## RF13 Visualización de contenido en realidad aumentada

| Campo | Especificación |
| --- | --- |
| Código | RF13 |
| Nombre del requisito | Visualización de contenido en realidad aumentada |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** La aplicación Android coloca el contenido 3D del capítulo sobre el QR físico reconocido por ARCore, con tamaño y posición definidos en centímetros respecto al marcador.

**Precondiciones**

- El dispositivo admite ARCore y concedió permiso de cámara.
- El capítulo y su modelo están disponibles; el QR impreso tiene la medida física configurada.

**Acciones desarrolladas por el sistema**

- Prepara la imagen QR como referencia de seguimiento y espera que ARCore la reconozca.
- Sitúa el modelo sobre el marcador y actualiza su visibilidad según el estado de seguimiento.
- Muestra narración y mensajes de orientación si el marcador se pierde.

**Acciones desarrolladas por el usuario**

- Enfoca el mismo QR con luz suficiente y mueve el teléfono lentamente.
- En vista docente puede ajustar tamaño, posición y giro sobre la página real.

**Poscondiciones.** El modelo se visualiza alineado al marcador mientras el seguimiento está disponible.

**Flujo alternativo.** Si ARCore no admite la imagen, se pierde el seguimiento o el modelo falla, se informa el problema; la lectura del texto sigue disponible cuando el capítulo ya cargó.

## RF14 Reproducción de audio narrativo

| Campo | Especificación |
| --- | --- |
| Código | RF14 |
| Nombre del requisito | Reproducción de audio narrativo |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** La aplicación permite escuchar la narración del capítulo. Prioriza el audio asociado al capítulo; si no existe, utiliza la voz de síntesis de Android en español cuando el dispositivo la ofrece.

**Precondiciones**

- El capítulo contiene texto narrativo o un archivo de audio.
- El dispositivo dispone de salida de audio; para descargar audio remoto hay conexión.

**Acciones desarrolladas por el sistema**

- Carga el clip local o remoto, o prepara TextToSpeech cuando falta audio grabado.
- Ofrece controles visibles de reproducir y pausar en la lectura y en AR.

**Acciones desarrolladas por el usuario**

- Pulsa «Escuchar» o «Pausar» en la vista del capítulo.
- Continúa la reproducción cuando lo desee.

**Poscondiciones.** La narración se escucha o queda pausada según la acción; al salir de la escena se detiene la voz generada.

**Flujo alternativo.** Si falla la descarga, intenta la voz del dispositivo; si tampoco hay voz española disponible, muestra una indicación para activarla en Android.

## RF15 Carga y visualización de modelos 3D GLB

| Campo | Especificación |
| --- | --- |
| Código | RF15 |
| Nombre del requisito | Carga y visualización de modelos 3D GLB |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** La aplicación descarga e importa el GLB del capítulo con glTFast, centra su geometría y ajusta su dimensión mayor al tamaño físico configurado. Puede ejecutar la animación elegida por el docente al tocar la vista AR.

**Precondiciones**

- El capítulo tiene una URL GLB válida o un prefab local configurado.
- La app puede obtener el recurso y ARCore reconoce el marcador para mostrarlo.

**Acciones desarrolladas por el sistema**

- Descarga e instancia el modelo, calcula sus límites y aplica escala, desplazamiento y giro.
- Si el GLB contiene el clip indicado, lo reproduce al toque; si no, informa la ausencia del clip.

**Acciones desarrolladas por el usuario**

- El docente sube el GLB y, si corresponde, escribe el nombre de la animación.
- El estudiante observa el modelo y toca la vista AR para activar la animación configurada.

**Poscondiciones.** El modelo queda preparado para visualizarse con sus ajustes de capítulo mientras el QR se siga.

**Flujo alternativo.** Si el GLB falta o no se puede importar, la app informa el fallo; solo usa contenido local si existe un prefab vinculado. Una animación no incluida en el GLB no puede reproducirse.

## RF16 Retorno al escáner QR desde la escena AR

| Campo | Especificación |
| --- | --- |
| Código | RF16 |
| Nombre del requisito | Retorno al escáner QR desde la escena AR |
| Fecha de elaboración | 04/11/2026 |
| Versión | 1.0 |

**Descripción del requisito.** Desde la escena de realidad aumentada, el usuario puede volver al escáner para leer otro capítulo sin reiniciar la aplicación.

**Precondiciones**

- La aplicación se encuentra en la escena AR (IU-14).

**Acciones desarrolladas por el sistema**

- Detiene la interacción de la escena actual y carga QRScanScene con la opción de abrir el escáner.
- Conserva la sesión estudiantil vigente o la vista docente activa según el flujo de acceso.

**Acciones desarrolladas por el usuario**

- Pulsa «Escanear otro QR».

**Poscondiciones.** Se muestra el escáner (IU-13) y el usuario puede leer otro marcador.

**Flujo alternativo.** Si la sesión caducó o la cámara no está disponible, el flujo solicita nuevo acceso o muestra la acción de recuperación correspondiente.

*Fuente: elaboración propia a partir de los repositorios BibliotecaAR, BibliotecaAR-backend y BiblitoecaAR-fronted, revisados el 04/11/2026.*
