# GLOSARIO DE TÉRMINOS

**Animación 3D:** Secuencia de movimientos que puede estar incluida en un modelo GLB. En la aplicación móvil se reproduce al tocar la pantalla cuando el archivo contiene el clip seleccionado.

**API REST:** Interfaz del backend que recibe solicitudes del panel web y de la aplicación móvil, y entrega los datos de docentes, estudiantes, libros y capítulos.

**AR Foundation:** Herramienta de Unity que integra las funciones de realidad aumentada de la aplicación móvil con ARCore en Android.

**ARCore:** Plataforma de realidad aumentada de Android que reconoce y sigue el marcador físico para ubicar el modelo 3D sobre la página.

**Asignación de cuentos:** Relación creada por el docente entre un estudiante y uno o varios libros. Los libros asignados y publicados aparecen en «Mis libros»; la asignación no impide abrir otros libros publicados mediante su QR.

**Backend:** Componente desarrollado con Django que aplica las reglas del sistema, expone la API y administra el acceso a los datos y recursos.

**Capítulo o escena narrativa:** Unidad de un cuento que reúne el texto narrativo, un código QR y, cuando corresponde, audio y un modelo 3D.

**Código de acceso estudiantil:** Clave personal generada por el docente para que el estudiante ingrese a la aplicación móvil; puede restablecerse si se extravía.

**Código QR:** Imagen que identifica un capítulo. La aplicación lee su contenido y consulta la API para obtener la escena correspondiente.

**GLB:** Formato binario de glTF utilizado para los modelos 3D; puede incluir geometría, materiales y animaciones en un solo archivo.

**glTFast:** Paquete de Unity que importa y carga los modelos GLB asociados a los capítulos.

**Marcador físico:** Código QR impreso sobre la página que sirve como referencia para colocar el modelo en realidad aumentada. Su ancho real se configura en centímetros.

**Modelo 3D:** Objeto tridimensional vinculado a un capítulo y visualizado sobre el marcador físico desde la cámara del teléfono.

**Panel docente:** Interfaz web desde la que el docente administra cuentos, capítulos, estudiantes, asignaciones y recursos multimedia.

**Progreso de lectura:** Registro de los capítulos que ha leído un estudiante, utilizado para mostrar su avance y permitirle continuar la lectura.

**Realidad aumentada (RA):** Tecnología que superpone contenido digital, como modelos 3D, sobre la imagen del entorno captada por la cámara.

**Reconocimiento facial experimental:** Opción de acceso que compara la imagen capturada con referencias de estudiantes registrados. En esta tesis no se considera una verificación biométrica robusta; el código personal sigue disponible.

**Seguimiento de imagen:** Proceso por el que ARCore estima la posición y orientación del marcador en la cámara para mantener el modelo alineado con la página. Es posterior a la lectura del QR.

**Síntesis de voz:** Lectura automática del texto narrativo mediante Android TextToSpeech cuando el capítulo no dispone de audio grabado.

**Supabase PostgreSQL:** Base de datos relacional en la nube donde se guardan los registros de docentes, estudiantes, cuentos, capítulos, asignaciones y avance.

**Supabase Storage:** Servicio de almacenamiento de archivos utilizado para portadas, audios, códigos QR y modelos 3D.

**Unity:** Motor con el que se desarrolla la aplicación Android que escanea los QR y presenta las escenas en realidad aumentada.

**ZXing:** Biblioteca que decodifica el contenido de los códigos QR captados por la cámara; la colocación del modelo corresponde a ARCore.
