# docugen

Automatiza la generación de documentos PDF a partir de datos en Excel, CSV u ODS.

## Requisitos

Python 3.14 y [uv](https://docs.astral.sh/uv/). Instalar las dependencias con:

```bash
uv sync
```

## Uso

```bash
uv run docugen                                                 # datos por defecto (data/personas.csv, columna Estado, valor Aprobado)
uv run docugen --archivo data/personas.xlsx --salida salida/   # elegir archivo y carpeta de salida
uv run docugen --columna Curso --valor Python                  # filtrar por otra columna y valor
uv run docugen --hoja Hoja2 --archivo datos.xlsx               # elegir una hoja del libro (xlsx/ods)
uv run docugen --info --archivo datos.ods                      # ver columnas, cantidad de registros y vista previa
```

El formato del archivo se detecta automáticamente por extensión: `.xlsx`, `.xls`, `.csv` y `.ods`.

Los PDFs se guardan en `salida/` (creada automáticamente).

## Plantillas

En vez del generador por defecto (reportlab), se puede renderizar una plantilla HTML (Jinja2) con WeasyPrint, usando las columnas del archivo como variables:

```bash
uv run docugen --plantilla templates/example/certificate.html --css templates/example/styles.css
uv run docugen --plantilla templates/example/certificate.html --columna Curso --valor Data\ Science
```

Hay una plantilla de ejemplo en `templates/example/`. El CSS es opcional.

## Interfaz gráfica

Interfaz experimental con Flet (en desarrollo):

```bash
uv run docugen-ui
```

Permite elegir archivo de datos, hoja, filtro, plantilla/CSS y carpeta de salida, con vista previa, barra de progreso y registro de errores.

## Configuración

Los últimos valores usados se guardan automáticamente en `config/config.json` y se reutilizan en la próxima ejecución. Los flags explícitos siempre tienen prioridad sobre la configuración guardada.

```bash
uv run docugen --reset-config   # restablecer la configuración a los valores por defecto
```

## Estructura

- `main.py` — punto de entrada alternativo (`python main.py`)
- `app/` — código: CLI, importadores (csv/excel/ods), generadores (reportlab/plantillas), servicios
- `config/` — configuración guardada (config.json)
- `data/` — datos de prueba en los 3 formatos (personas.csv, personas.xlsx, personas.ods)
- `templates/` — plantillas HTML (Jinja2)
- `salida/` — documentos generados

## Roadmap

Ver [ROADMAP.md](ROADMAP.md).

## Dependencias

`uv sync` instala todo: reportlab, weasyprint, jinja2, pandas, openpyxl, flet, pillow.
