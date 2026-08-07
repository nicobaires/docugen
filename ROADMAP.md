# 🗺️ Roadmap

DocuGen nace como un motor de generación de documentos a partir de datos estructurados (Excel, CSV, bases de datos, APIs, etc.). El objetivo no es generar únicamente certificados, sino construir una herramienta flexible capaz de completar cualquier plantilla con información proveniente de distintas fuentes.

---

## 🚀 v0.0 - Proof of Concept

Primer prototipo funcional.

### Objetivos

* [x] Leer un archivo Excel (.xlsx)
* [x] Filtrar registros
* [x] Generar un PDF por cada fila
* [x] Crear automáticamente la carpeta de salida
* [x] Nombrar automáticamente los archivos generados

---

## 📊 v0.1 - Importación de datos

El objetivo es convertir cualquier origen de datos en un DataFrame de Pandas.

### Soporte inicial

* [x] Excel (.xlsx)
* [x] CSV
* [x] LibreOffice (.ods)
* [x] Seleccionar hoja del libro
* [x] Vista previa de los datos
* [x] Mostrar cantidad de registros
* [x] Filtrado por columnas (Estado, Curso, Empresa, etc.)

---

## 📄 v0.2 - Motor de plantillas

Separar completamente los datos del diseño.

### Funcionalidades

* [x] Plantillas HTML + CSS
* [x] Renderizado mediante Jinja2
* [x] Conversión HTML → PDF con WeasyPrint
* [x] Variables dinámicas

Ejemplo:

```html
{{ Nombre }}

{{ Documento }}

{{ Curso }}

{{ Fecha }}
```

---

## ⚙️ v0.3 - Configuración

Guardar automáticamente la configuración del proyecto.

### Funcionalidades

* [x] Último archivo utilizado
* [x] Última plantilla utilizada
* [x] Carpeta de salida
* [x] Configuración de filtros
* [x] Preferencias del usuario

---

# 🎉 v1.0

Primera versión estable.

### Características

* [ ] Selección de archivo
* [ ] Selección de plantilla
* [ ] Generación masiva de documentos
* [ ] Barra de progreso
* [ ] Registro de errores
* [ ] Interfaz gráfica con Flet

---

# 🔗 v1.1 - Nuevos importadores

Agregar nuevos orígenes de datos.

* [ ] Google Sheets
* [ ] SQLite
* [ ] MySQL
* [ ] PostgreSQL

Todos los importadores entregan un DataFrame como estructura común.

---

# 🧩 v1.2 - Mapeo de campos

Eliminar la dependencia de nombres específicos de columnas.

Ejemplo:

| Campo de la plantilla | Columna del origen |
| --------------------- | ------------------ |
| Nombre                | Apellido y Nombre  |
| Documento             | DNI                |
| Curso                 | Capacitación       |
| Fecha                 | Fecha Final        |

---

# 🎨 v1.3 - Plantillas reutilizables

Organizar las plantillas como proyectos independientes.

```
plantillas/

certificado/

credencial/

constancia/

invitacion/
```

Cada plantilla contendrá:

* HTML
* CSS
* Imágenes
* Tipografías
* Recursos propios

---

# 🖱️ v2.0 - Editor visual

Primer editor visual de plantillas.

### Objetivos

* [ ] Mostrar la plantilla en pantalla
* [ ] Seleccionar un campo
* [ ] Insertarlo haciendo clic con el mouse
* [ ] Guardar automáticamente la posición

Sin escribir coordenadas manualmente.

---

# ✨ v2.1 - Editor avanzado

* [ ] Arrastrar campos
* [ ] Redimensionar
* [ ] Alinear
* [ ] Duplicar
* [ ] Eliminar

---

# 🎨 v2.2 - Estilos

Configurar visualmente cada campo.

* [ ] Fuente
* [ ] Tamaño
* [ ] Color
* [ ] Negrita
* [ ] Cursiva
* [ ] Alineación
* [ ] Espaciado

---

# 🤖 v3.0 - Automatización

Automatizar el proceso completo.

* [ ] Generación de ZIP
* [ ] Envío por correo
* [ ] Código QR
* [ ] Numeración automática
* [ ] Firma digital
* [ ] Registro de documentos generados

---

# 📚 v4.0 - Motor de documentos

DocuGen deja de ser un generador de certificados y se convierte en un motor de generación documental.

Ejemplos de uso:

* Certificados
* Diplomas
* Constancias
* Credenciales
* Invitaciones
* Etiquetas
* Turnos médicos
* Cartas personalizadas
* Recibos
* Formularios

---

# 🌎 v5.0 - Ecosistema

Crear una comunidad alrededor del proyecto.

* [ ] Biblioteca de plantillas
* [ ] Importar / Exportar plantillas
* [ ] Compartir diseños
* [ ] Plugins
* [ ] API pública

---

# 💡 Ideas futuras

* DOCX como formato de salida
* HTML como formato de salida
* PNG/JPG como formato de salida
* Integración con servicios en la nube
* Automatización mediante APIs
* Integración con Telegram y WhatsApp
* Variables calculadas
* Código de barras
* Firma electrónica

---

## Filosofía del proyecto

DocuGen no pretende ser únicamente un generador de certificados.

Su objetivo es convertirse en un **motor de generación de documentos**, donde los datos, las plantillas y el formato de salida estén completamente desacoplados.

```
Origen de datos
       │
       ▼
DataFrame (Pandas)
       │
       ▼
Motor DocuGen
       │
       ▼
Plantilla (HTML + CSS)
       │
       ▼
Documento generado
```

La plantilla define **cómo** se verá el documento.

Los datos definen **qué** contendrá.

El motor simplemente une ambos mundos.
