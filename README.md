# certificado

Generador de certificados PDF a partir de un archivo Excel.

## Uso

```bash
python main.py                         # datos por defecto (data/personas.xlsx, estado Aprobado)
python main.py --estado "En curso"     # filtrar por otro estado
python main.py --archivo ruta.xlsx --salida salida/ --estado Reprobado
```

Los PDFs se guardan en `salida/` (creada automáticamente).

## Estructura

Ver `ESTRUCTURA.md`.

## Dependencias

Instalar con `uv sync` (reportlab, pandas, openpyxl, flet, weasyprint, pillow).
