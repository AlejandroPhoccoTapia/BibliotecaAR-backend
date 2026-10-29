# Transiciones entre interfaces de BibliotecaAR

Las tablas siguientes resumen los recorridos principales del panel docente y de la aplicación Android. Los códigos corresponden al [catálogo de interfaces](catalogo-interfaces.md) y a los diagramas de [navegabilidad web](diagramas/07-navegacion-panel-docente.png) y [navegabilidad móvil](diagramas/08-navegacion-app-movil.png). Las acciones que solo actualizan datos o muestran mensajes conservan la misma interfaz.

## Panel docente web

| Origen | Acción | Destino |
| --- | --- | --- |
| IU-01 | Iniciar sesión o registrar una cuenta docente correctamente. | IU-02 |
| IU-01 | Introducir credenciales inválidas o datos de registro incorrectos. | IU-01, con mensaje de error |
| IU-02 | Elegir «Nuevo libro» o editar un libro desde su tarjeta. | IU-03 |
| IU-02 | Abrir un libro del catálogo. | IU-04 |
| IU-03 | Guardar el libro. | IU-04, detalle del libro guardado |
| IU-03 | Volver sin guardar. | IU-02 si es nuevo; IU-04 si se editaba |
| IU-04 | Volver al catálogo o eliminar el libro tras confirmar. | IU-02 |
| IU-04 | Elegir «Editar libro». | IU-03 |
| IU-04 | Crear un capítulo o editar uno existente. | IU-05 |
| IU-05 | Guardar el capítulo o volver. | IU-04 |
| IU-04 | Consultar el QR, descargar el PDF o abrir la vista 3D. | IU-04; son acciones dentro del detalle |
| IU-02 | Abrir la pestaña «Estudiantes». | IU-06 |
| IU-06 | Registrar un estudiante o editar su perfil. | IU-07 |
| IU-07 | Guardar un estudiante nuevo. | IU-06 con IU-08 superpuesto |
| IU-07 | Guardar cambios de un estudiante existente o volver. | IU-06 |
| IU-06 | Generar o restablecer un código de acceso. | IU-06 con IU-08 superpuesto |
| IU-08 | Cerrar el diálogo después de consultar o copiar el código. | IU-06 |
| IU-06 | Abrir la pestaña «Biblioteca». | IU-02 |
| IU-02 a IU-07 | Cerrar sesión; confirmar la salida si hay cambios sin guardar. | IU-01 |

*Tabla. Transiciones principales del panel docente web. Fuente: elaboración propia a partir de la implementación de BibliotecaAR.*

## Aplicación móvil Android

| Origen | Acción | Destino |
| --- | --- | --- |
| Apertura de la app | No hay sesión de estudiante recordada. | IU-09 |
| Apertura de la app | El estudiante tiene una sesión recordada y vigente. | IU-10 |
| IU-09 | Entrar con código personal o acceso facial aceptado. | IU-10 |
| IU-09 | El código o el rostro no se reconoce. | IU-09, con opción de reintentar o usar código |
| IU-09 | Elegir «Docente». | IU-15 |
| IU-10 | Abrir un libro asignado o explorado. | IU-11 |
| IU-10 | Elegir «Continuar leyendo». | IU-12, tras cargar el capítulo |
| IU-11 | Abrir un capítulo. | IU-12 |
| IU-11 | Volver a la biblioteca. | IU-10 |
| IU-12 | Volver al libro. | IU-11 |
| IU-12 | Escuchar, pausar o marcar el capítulo como leído. | IU-12 |
| IU-10 / IU-12 | Elegir «Escanear QR» o «Ver en AR · Escanear». | IU-13 |
| IU-13 | Leer un QR de un capítulo disponible. | IU-14 |
| IU-13 | Denegar la cámara o no lograr leer el código. | IU-13, con indicaciones y reintento |
| IU-13 | Elegir «Biblioteca» o «Salir vista docente». | IU-10 si hay estudiante con sesión; IU-09 en caso contrario |
| IU-14 | Elegir «Escanear otro QR». | IU-13 |
| IU-14 | Leer, escuchar, pausar o marcar el capítulo como leído. | IU-14 |
| IU-10 | Elegir «Cambiar estudiante». | IU-09 |
| IU-10 | Elegir «Ajustar modelos sobre la página». | IU-15 |
| IU-15 | Ingresar credenciales docentes válidas. | IU-13, listo para escanear el capítulo |
| IU-15 | Elegir «Volver» o fallar la autenticación. | IU-10 o IU-09 al volver; IU-15 si falla |
| IU-16 | Elegir «Escanear capítulo». | IU-13 |
| IU-16 | Elegir «Salir del modo docente». | IU-10 si hay estudiante con sesión; IU-09 en caso contrario |
| IU-14 | En vista docente, elegir «Ajustar modelo». | IU-17, panel sobre la escena AR |
| IU-17 | Ajustar valores, guardar o deshacer cambios. | IU-17 |
| IU-17 | Elegir «Ver modelo». | IU-14 |
| IU-10 a IU-12 | La sesión del estudiante vence durante una consulta protegida. | IU-09 |

*Tabla. Transiciones principales de la aplicación móvil. Fuente: elaboración propia a partir de la implementación de BibliotecaAR.*

`IU-16` aparece cuando se abre la escena de escaneo con una vista docente todavía activa y sin una orden inmediata de escanear. Tras iniciar sesión como docente desde `IU-15`, el código abre directamente el escáner `IU-13`. La apertura de la app no tiene un código IU propio porque no existe una pantalla de arranque independiente en el catálogo.
