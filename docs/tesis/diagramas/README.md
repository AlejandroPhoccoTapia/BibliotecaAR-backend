# Diagramas para la tesis de BibliotecaAR

Estas figuras se prepararon a partir del código de los tres repositorios de BibliotecaAR y de la comparación visual de los tres borradores de tesis entregados el 29 de octubre de 2026. Los PDF de los compañeros sirvieron para identificar **tipos de figuras**; los procesos y las entidades de estas figuras corresponden al proyecto de Alejandro Josué Phocco Tapia.

El [catálogo de interfaces](../catalogo-interfaces.md) usa los códigos IU que aparecen en los diagramas de navegabilidad. También existe una [versión Word](../catalogo-interfaces.docx) lista para copiar en la tesis.

## Qué hay en los borradores

| Tipo de figura | Tesis de Alejandro | Referencia 1 | Referencia 2 | Acción |
| --- | --- | --- | --- | --- |
| Esquema general de aplicación | Sí | Sí | Sí | Conservar el existente. |
| Tecnologías | Sí | Sí | Sí | Conservar el existente. |
| Modelo de datos | Sí, desactualizado | Sí | Sí | Reemplazar por el ER actualizado. |
| Arquitectura por capas | Sí | Sí | No se identifica igual | Conservar y revisar etiquetas. |
| Paquetes | Aparece el título, sin figura | Sí | Sí | Insertar el diagrama de paquetes ya preparado. |
| Clases | No | Sí | No se identifica | Añadir la figura de clases principales. |
| Secuencias | No | Sí | Sí | Añadir las dos secuencias de BibliotecaAR. |
| Actividades | No | Sí | Sí | Añadir las dos actividades de BibliotecaAR. |
| Navegación | No | Sí | Sí | Añadir los recorridos web y móvil si se documentan ambas interfaces. |

«No se identifica» solo describe los PDF comparados, no implica que el tipo de diagrama sea obligatorio u opcional en una tesis. La selección y numeración final deben ajustarse a la guía y al asesor.

## Figuras listas para insertar

Cada figura tiene un PNG para Word, un SVG para conservar nitidez al ampliar y un archivo PlantUML (`.puml`) editable. Los nombres numerados ordenan esta carpeta; **no son números definitivos de figura**.

| Figura sugerida | PNG | SVG | Fuente editable | Qué explica |
| --- | --- | --- | --- | --- |
| Modelo entidad–relación actualizado | [PNG](01-entidad-relacion.png) | [SVG](01-entidad-relacion.svg) | [PlantUML](01-entidad-relacion.puml) | Libros, capítulos, estudiantes, asignaciones, sesiones y avance. |
| Clases principales del dominio | [PNG](02-clases-dominio.png) | [SVG](02-clases-dominio.svg) | [PlantUML](02-clases-dominio.puml) | Modelos Django y asociaciones. |
| Secuencia: creación de capítulo y QR | [PNG](03-secuencia-crear-capitulo-qr.png) | [SVG](03-secuencia-crear-capitulo-qr.svg) | [PlantUML](03-secuencia-crear-capitulo-qr.puml) | Panel docente, API, guardado, QR y PDF imprimible. |
| Secuencia: escaneo y lectura AR | [PNG](04-secuencia-escaneo-lectura-ar.png) | [SVG](04-secuencia-escaneo-lectura-ar.svg) | [PlantUML](04-secuencia-escaneo-lectura-ar.puml) | Unity, API, archivos, seguimiento AR y progreso. |
| Actividad: acceso del estudiante | [PNG](05-actividad-acceso-estudiante.png) | [SVG](05-actividad-acceso-estudiante.svg) | [PlantUML](05-actividad-acceso-estudiante.puml) | Sesión recordada, código, rostro y biblioteca. |
| Actividad: escaneo y lectura AR | [PNG](06-actividad-escanear-y-leer-ar.png) | [SVG](06-actividad-escanear-y-leer-ar.svg) | [PlantUML](06-actividad-escanear-y-leer-ar.puml) | Permisos, QR, carga, seguimiento y lectura. |
| Navegación: panel docente | [PNG](07-navegacion-panel-docente.png) | [SVG](07-navegacion-panel-docente.svg) | [PlantUML](07-navegacion-panel-docente.puml) | Pantallas React y acceso a sus formularios. |
| Navegación: app móvil | [PNG](08-navegacion-app-movil.png) | [SVG](08-navegacion-app-movil.svg) | [PlantUML](08-navegacion-app-movil.puml) | Acceso estudiantil y docente, biblioteca, escáner y AR. |

El [diagrama de paquetes del sistema completo](../../diagrama-paquetes.md) ya estaba documentado. Para insertar una sola figura en la tesis, usa su [versión vertical en PNG](../../diagrama-paquetes-sistema-vertical.png) o [SVG](../../diagrama-paquetes-sistema-vertical.svg), con [PlantUML editable](../../diagrama-paquetes-sistema-vertical.puml). El [detalle móvil en PNG](../../diagrama-paquetes-app-movil.png), [SVG](../../diagrama-paquetes-app-movil.svg) y [PlantUML](../../diagrama-paquetes-app-movil.puml) es opcional. En el PDF de Alejandro, la figura de paquetes va donde ahora solo aparece ese encabezado.

## Orden sugerido en el capítulo de diseño

1. Conservar el esquema general y las tecnologías existentes.
2. Sustituir el ER anterior por `01-entidad-relacion` y explicar las tablas `StudentSession` y `StudentReadingProgress`, que ya existen en el código.
3. Poner el diagrama de paquetes vertical del sistema después de la arquitectura; usar el detalle móvil solo si el texto explica sus módulos internos.
4. Añadir clases, dos secuencias y dos actividades en la sección de diseño de software.
5. Añadir las dos figuras de navegación junto a la descripción de las interfaces. Si el documento solo trata una interfaz en detalle, usar solo la que corresponda.

**Leyendas sugeridas:** “Modelo entidad–relación de BibliotecaAR”, “Diagrama de clases principales de BibliotecaAR”, “Secuencia de creación de capítulo y QR”, “Secuencia de escaneo y lectura en realidad aumentada”, “Actividad de acceso del estudiante”, “Actividad de escaneo y lectura AR”, “Navegabilidad del panel docente” y “Navegabilidad de la aplicación móvil”. En el pie de figura se puede indicar “Fuente: elaboración propia a partir de la implementación de BibliotecaAR”.

## Límites de interpretación

- Las figuras muestran la implementación disponible, no resultados de pruebas con estudiantes ni un sistema de reconocimiento facial validado. El acceso por rostro actual es experimental; el código personal sigue siendo una alternativa.
- Los modelos de Django son clases del dominio y tablas persistidas. `Scene` es un capítulo, distinto de una escena Unity.
- El ER presenta atributos relevantes para mantener la figura legible; el detalle completo está en `catalog/models.py`.
- Los diagramas de navegación resumen rutas principales. Los botones de volver, cerrar sesión y cambiar de estudiante no se dibujan uno por uno.
- El escaneo de QR, la consulta del capítulo y el seguimiento AR son etapas distintas. La app móvil llama a la API Django; no consulta PostgreSQL directamente.
- Los PNG se verificaron visualmente. Para editar cualquiera de las figuras, abrir su `.puml` con PlantUML y volver a exportar PNG o SVG.
