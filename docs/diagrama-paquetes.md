# Diagrama de paquetes de BibliotecaAR

Este es el diagrama de paquetes **general** del proyecto. Los tres contenedores grandes corresponden a los tres repositorios; los bloques internos agrupan código con una responsabilidad común. Las flechas discontinuas indican que el paquete de origen **depende** del paquete al que apuntan. No representan el orden temporal de uso de la aplicación.

```mermaid
flowchart LR
    subgraph WEB["«paquete» Panel docente · React"]
        direction TB
        W_UI["Interfaz y formularios<br/>App.jsx · components/"]
        W_PREVIEW["Vista previa 3D<br/>GlbPreview.jsx"]
        W_API["Cliente HTTP<br/>api.js"]
        W_UI -.-> W_PREVIEW
        W_UI -.-> W_API
    end

    subgraph SERVER["«paquete» Backend · Django"]
        direction TB
        B_API["Rutas y vistas API<br/>catalog/urls.py · views.py"]
        B_AUTH["Autenticación e identificación<br/>student_auth.py · teacher_mobile_auth.py<br/>face_recognition.py"]
        B_CATALOG["Catálogo y progreso<br/>models.py · serializers.py · validators.py"]
        B_QR["QR y PDF imprimible<br/>Scene.save() · qr_pdf.py"]
        B_API -.-> B_AUTH
        B_API -.-> B_CATALOG
        B_API -.-> B_QR
        B_AUTH -.-> B_CATALOG
        B_QR -.-> B_CATALOG
    end

    subgraph MOBILE["«paquete» Aplicación Android · Unity"]
        direction TB
        M_ACCESS["Acceso, biblioteca y escáner<br/>StudentAppFlow.cs · QRCodeScanner.cs"]
        M_SESSION["Sesión y peticiones HTTP<br/>StudentAppSession.cs · TeacherPreviewSession.cs"]
        M_AR["Lectura y coordinación AR<br/>ARSceneController.cs · ARSceneExperienceUI.cs"]
        M_TRACK["Seguimiento y contenido 3D<br/>QRTrackedImagePlacer.cs · ARStoryInteraction.cs"]
        M_ACCESS -.-> M_SESSION
        M_ACCESS -.-> M_AR
        M_AR -.-> M_SESSION
        M_AR -.-> M_TRACK
    end

    W_API -. "HTTP: /api/teacher/*" .-> B_API
    M_SESSION -. "HTTP: acceso, biblioteca y progreso" .-> B_API
    M_AR -. "HTTP: capítulo y recursos AR" .-> B_API
```

## Lectura del diagrama

1. El **panel docente** usa `src/api.js` para crear y editar libros, capítulos y estudiantes mediante la API. La vista previa GLB funciona en el navegador, pero la experiencia AR se ejecuta en Unity.
2. El **backend** recibe las solicitudes, aplica autenticación y permisos, valida los datos y consulta el catálogo. `Scene` representa un capítulo; genera su identificador QR y el PNG. `qr_pdf.py` genera la hoja lista para imprimir con la medida física guardada.
3. La **app móvil** permite acceso por código o rostro, muestra la biblioteca y escanea el QR. `ARSceneController` consulta el capítulo y coordina texto, audio, modelo y seguimiento de imagen. La sesión y las peticiones se gestionan en los scripts de acceso docente/estudiantil y en el propio controlador AR.
4. La dependencia entre repositorios es **HTTP hacia Django**. Ni React ni Unity consultan directamente PostgreSQL/SQLite. Los archivos de audio, modelos e imágenes se obtienen mediante las URLs que devuelve la API.

## Correspondencia con los repositorios

| Paquete principal | Repositorio | Código representativo |
| --- | --- | --- |
| Panel docente | [`BiblitoecaAR-fronted`](https://github.com/AlejandroPhoccoTapia/BiblitoecaAR-fronted) | `src/App.jsx`, `src/components/`, `src/api.js`, `src/lib/forms.js` |
| Backend | [`BibliotecaAR-backend`](https://github.com/AlejandroPhoccoTapia/BibliotecaAR-backend) | `catalog/`, `config/` |
| Aplicación Android | [`BibliotecaAR`](https://github.com/AlejandroPhoccoTapia/BibliotecaAR) | `Assets/Scripts/`, `Assets/Scenes/` |

La base de datos y el almacenamiento de archivos **no se dibujan como paquetes de código**: son infraestructura. En desarrollo se usa SQLite y media local; el despliegue está configurado para PostgreSQL y almacenamiento de Supabase. Si necesitas representar Vercel, Render, Supabase y el teléfono como máquinas o servicios, corresponde hacer un **diagrama de despliegue** aparte.

Para una explicación general de la arquitectura en la tesis, **este único diagrama de paquetes es suficiente**. Un segundo diagrama interno de Django o Unity solo aporta valor si el documento exige describir sus dependencias con más detalle; no conviene multiplicar diagramas que repitan las mismas relaciones.
