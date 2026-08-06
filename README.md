# docugen

Automatiza la generación de documentos PDF a partir de datos en Excel, CSV u ODS.

## Uso

```bash
python main.py                         # datos por defecto (data/personas.xlsx, estado Aprobado)
python main.py --estado "En curso"     # filtrar por otro estado
python main.py --archivo ruta.csv --salida salida/ --estado Reprobado
```

El formato del archivo se detecta automáticamente por extensión: `.xlsx`, `.xls`, `.csv` y `.ods`.

Los PDFs se guardan en `salida/` (creada automáticamente).

## Estructura

Ver `ESTRUCTURA.md`.

## Dependencias

Instalar con `uv sync` (reportlab, pandas, openpyxl, flet, weasyprint, pillow).
