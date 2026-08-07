import re
from pathlib import Path

import pandas as pd

from app.templates.renderer import render_dict_to_pdf


def _nombre_archivo_seguro(nombre):
    nombre_limpio = str(nombre).strip().replace(" ", "_")
    return re.sub(r"[^\w-]", "_", nombre_limpio)


def generar_pdfs_con_plantilla(df, plantilla, carpeta_salida="salida", css=None, on_progreso=None):
    plantilla = Path(plantilla)
    carpeta = Path(carpeta_salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    archivos_generados = []
    total = len(df)

    for i, (idx, row) in enumerate(df.iterrows()):
        if on_progreso:
            on_progreso(i + 1, total)
        contexto = {col: ("" if pd.isna(valor) else valor) for col, valor in row.items()}
        nombre = contexto.get("Nombre") or f"fila_{idx}"
        nombre_limpio = _nombre_archivo_seguro(nombre)
        ruta_pdf = carpeta / f"Certificado_{nombre_limpio}.pdf"

        render_dict_to_pdf(
            context=contexto,
            template_dir=plantilla.parent,
            template_name=plantilla.name,
            css_path=Path(css) if css else None,
            output_path=ruta_pdf,
        )
        archivos_generados.append(ruta_pdf)

    return archivos_generados
