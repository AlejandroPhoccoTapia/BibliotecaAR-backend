# Conclusiones y recomendaciones de BibliotecaAR

> **Borrador para incorporar a la tesis después de completar las pruebas de campo.** Las conclusiones 6, 7, 8 y 9, relacionadas con la app, la visualización AR y el resultado global, se redactan con el alcance que permite la evidencia actual. Deben actualizarse con el resultado observado de los casos CP-03 a CP-08 del capítulo IV. No se debe sustituir un resultado faltante por un porcentaje supuesto.

## Conclusiones

1. **Objetivo específico 1.** Se logró analizar los requerimientos funcionales y técnicos del sistema de narrativa virtual mediante realidad aumentada, gracias a la identificación de las necesidades de gestión docente, acceso estudiantil, consulta de capítulos y presentación de contenido multimedia. Como resultado, se definieron dieciséis requisitos funcionales, descritos en el catálogo y relacionados con sus módulos en la Tabla 4.1.

2. **Objetivo específico 2.** Se logró diseñar la arquitectura del sistema, gracias a la separación entre el panel web React, la API Django y la aplicación móvil Unity, con persistencia y almacenamiento configurables. Como resultado, se documentaron las responsabilidades y las interfaces de intercambio entre los tres repositorios. La conexión efectiva con PostgreSQL y Supabase Storage requiere aún la prueba CP-07.

3. **Objetivo específico 3.** Se logró desarrollar el módulo web de gestión docente para libros, capítulos, estudiantes y recursos multimedia, gracias a los formularios, listados, asignaciones y vista previa del modelo. Como resultado comprobable, las siete pruebas automáticas del frontend se aprobaron y la compilación de producción finalizó correctamente. Estas pruebas no miden la facilidad de uso del panel por parte de docentes.

4. **Objetivo específico 4.** Se logró implementar el backend para gestionar la información y responder a las solicitudes de los clientes, gracias a los modelos, validaciones y endpoints de Django. Como resultado, se aprobaron las 51 pruebas automáticas del servidor con SQLite y archivos locales de prueba. La persistencia en Supabase y la recuperación de archivos remotos siguen pendientes de CP-07.

5. **Objetivo específico 5.** Se logró integrar el registro docente, el código personal del estudiante, el endpoint de acceso facial experimental y el QR único por capítulo, gracias a los mecanismos de autenticación, identificación y generación de códigos del backend. Las pruebas automáticas cubren esos flujos a nivel de API; todavía no se ha medido la precisión del reconocimiento facial con estudiantes reales ni el porcentaje de lectura de QR con la cámara.

6. **Objetivo específico 6.** Se logró desarrollar en Unity el flujo de escaneo QR y consulta de capítulos por API, gracias a la conexión entre las escenas de escáner y realidad aumentada y al endpoint de búsqueda de capítulos. El recorrido instalado en un teléfono aún debe verificarse con CP-03 y CP-08; por ello no se afirma una tasa de escaneo ni un funcionamiento móvil completo.

7. **Objetivo específico 7.** Se logró incorporar componentes para presentar texto, audio y modelos GLB asociados a cada capítulo, gracias a la lectura de la respuesta de la API, el sistema de audio y la carga de modelos en Unity. Su visualización y reproducción conjunta sobre una página física todavía requieren CP-04, CP-05 y CP-06 en un dispositivo compatible con ARCore.

8. **Objetivo específico 8.** Se evaluó la gestión de contenidos, la validación de archivos, la consulta de escenas y las reglas de progreso mediante 51 pruebas del backend y 7 del frontend, todas aprobadas en el entorno local. La evaluación del objetivo permanece parcial, porque faltan la comprobación del almacenamiento remoto y las pruebas de visualización aumentada en el teléfono.

9. **Objetivo general.** Se logró desarrollar un prototipo integrado de narrativa de cuentos virtuales con realidad aumentada, gracias a la articulación del panel docente, la API y el cliente Unity en torno a capítulos identificados por QR. Las pruebas disponibles acreditan la lógica local del servidor y del panel, pero la validación del objetivo general y de la hipótesis requiere ejecutar el recorrido completo con la app instalada, los servicios desplegados y un marcador impreso. No se dispone aún de un resultado sobre comprensión lectora, motivación o satisfacción de estudiantes.

## Recomendaciones

1. Ejecutar los casos CP-03 a CP-06 y CP-08 en al menos un teléfono compatible con ARCore, usando varios QR impresos a la escala configurada y modelos GLB de dimensiones distintas. Registrar los intentos, las condiciones de iluminación y las pérdidas de seguimiento para conocer la confiabilidad real del escaneo y de la escena aumentada.

2. Completar CP-07 con Render, Supabase PostgreSQL y Supabase Storage configurados, y conservar evidencia de escritura y lectura desde dos sesiones. Repetir el caso después de reiniciar el backend para distinguir la persistencia remota de los datos temporales locales.

3. Evaluar el acceso facial con un conjunto de estudiantes voluntarios, consentimiento adecuado y condiciones de luz variadas. Mantener el código personal como alternativa y evitar presentar el método experimental como autenticación biométrica robusta hasta medir sus errores y resolver el tratamiento privado de las fotografías.

4. Realizar una prueba de uso con docentes y estudiantes para observar si comprenden el flujo de publicación, la impresión del QR, la lectura del capítulo, los controles de audio y el retorno al escáner. Utilizar un instrumento definido antes de afirmar mejoras en motivación, comprensión o satisfacción.

5. Revisar la carga de la vista previa GLB del panel, que genera una advertencia de tamaño en la compilación web, y comprobar su tiempo de apertura en conexiones reales. Revisar también la eliminación y recuperación de archivos remotos ante fallos de red, porque las operaciones de base de datos y almacenamiento de objetos no forman una única transacción.
