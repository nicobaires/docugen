# docugen

Automatiza la generación de documentos PDF a partir de datos en Excel, CSV u ODS.

## Uso

```bash
python main.py                                    # datos por defecto (data/personas.csv, columna Estado, valor Aprobado)
python main.py --columna Curso --valor Python     # filtrar por otra columna y valor
python main.py --hoja Hoja2 --archivo datos.xlsx  # elegir una hoja del libro (xlsx/ods)
python main.py --info --archivo datos.ods         # ver columnas, cantidad de registros y vista previa
```

El formato del archivo se detecta automáticamente por extensión: `.xlsx`, `.xls`, `.csv` y `.ods`.

Los PDFs se guardan en `salida/` (creada automáticamente).

## Plantillas

En vez del generador por defecto (reportlab), se puede renderizar una plantilla HTML (Jinja2) con WeasyPrint, usando las columnas del archivo como variables:

```bash
python main.py --plantilla templates/example/certificate.html --css templates/example/styles.css
```

Hay una plantilla de ejemplo en `templates/example/`. El CSS es opcional.

## Estructura

Ver `ESTRUCTURA.md`.

## Roadmap

Ver [ROADMAP.md](ROADMAP.md).

## Dependencias

Instalar con `uv sync` (reportlab, weasyprint, jinja2, pandas, openpyxl, flet, pillow).
