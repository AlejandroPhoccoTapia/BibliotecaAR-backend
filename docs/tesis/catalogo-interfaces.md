# Catálogo de interfaces de BibliotecaAR

BibliotecaAR tiene un panel web para docentes y una aplicación Android para estudiantes. La aplicación móvil también ofrece una vista docente para ajustar el modelo 3D sobre la página. Las interfaces se identifican con códigos `IU-nn` para relacionarlas con el [diagrama de navegabilidad web](diagramas/07-navegacion-panel-docente.png) y el [diagrama de navegabilidad móvil](diagramas/08-navegacion-app-movil.png). Los códigos `IU-01` a `IU-08` pertenecen al panel web; `IU-09` a `IU-17`, a la aplicación móvil.

| Código | Interfaz | Función principal |
| --- | --- | --- |
| IU-01 | Acceso y registro docente | Permite iniciar sesión o crear una cuenta docente desde el panel web. |
| IU-02 | Biblioteca de libros | Muestra los libros del catálogo y permite buscarlos, filtrarlos, ordenarlos, abrirlos o crear uno nuevo. |
| IU-03 | Formulario de libro | Permite crear o editar título, descripción, portada y estado de publicación. |
| IU-04 | Detalle de libro | Presenta sus capítulos y permite editar contenido, consultar el QR, descargar el PDF imprimible y abrir la vista previa 3D del GLB. |
| IU-05 | Formulario de capítulo | Permite editar texto, audio, modelo 3D, animación al toque y medidas de colocación sobre la página. |
| IU-06 | Lista de estudiantes | Permite buscar y filtrar perfiles, abrir su edición y generar un nuevo código de acceso. |
| IU-07 | Formulario de estudiante | Permite registrar o editar nombre, aula, fotografía, estado y libros asignados. |
| IU-08 | Código de acceso generado | Ventana emergente que muestra el código nuevo una sola vez y permite copiarlo. |
| IU-09 | Acceso del estudiante | Permite identificarse con el código personal o el acceso facial experimental y elegir si se recuerda el dispositivo. |
| IU-10 | Biblioteca del estudiante | Muestra libros asignados, libros explorados y la opción de retomar la última lectura; permite abrir el escáner QR. |
| IU-11 | Libro y capítulos | Muestra la descripción del libro, la lista de capítulos y el estado de lectura de cada uno. |
| IU-12 | Lectura del capítulo | Presenta el texto, permite escuchar o pausar el audio, marcar el capítulo como leído y abrir la experiencia AR. |
| IU-13 | Escáner QR | Usa la cámara para leer el código del capítulo y muestra indicaciones o acciones de recuperación si falla el escaneo. |
| IU-14 | Escena de realidad aumentada | Sitúa el modelo 3D sobre el marcador reconocido y ofrece narración, audio, mensajes de seguimiento y registro del avance. |
| IU-15 | Acceso docente móvil | Autentica al docente para la vista de ajuste del modelo sobre una página real. |
| IU-16 | Vista docente activa | Permite iniciar el escaneo del capítulo que se desea ajustar o salir de la vista docente. |
| IU-17 | Ajuste del modelo en AR | Panel superpuesto a la escena AR que permite modificar medida del marcador, tamaño, posición y giro del modelo, guardar y volver a verlo. |

**Criterio de catalogación.** `IU-08` es una ventana emergente y `IU-17` es un panel superpuesto. Los formularios de inicio y registro docente comparten `IU-01`; el acceso por código y por rostro comparten `IU-09`. El visor GLB, la tarjeta QR y la descarga PDF son acciones dentro de `IU-04` o `IU-05`, no pantallas independientes. Los estados de carga y error aparecen dentro de las interfaces correspondientes. El acceso facial está implementado como función experimental y no equivale a una validación biométrica de producción.

*Fuente: elaboración propia a partir del código de BibliotecaAR, BiblitoecaAR-fronted y BibliotecaAR-backend, revisado el 29 de octubre de 2026.*

Las [tablas de transiciones](transiciones-interfaces.md) usan estos mismos códigos para explicar qué acción lleva de una interfaz a otra.
