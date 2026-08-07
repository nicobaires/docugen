#!/usr/bin/env python3
"""Script de ejemplo que toma data/personas.csv y renderiza una plantilla para cada fila.

Uso:
    python scripts/run_template_example.py --archivo data/personas.csv --salida salida/templates_example

"""
from pathlib import Path
import argparse
import pandas as pd
import re

from app.templates.renderer import render_dict_to_pdf


def safe_name(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]", "_", str(s))
    return s


def main():
    parser = argparse.ArgumentParser(description="Ejecutar ejemplo de template")
    parser.add_argument("--archivo", default=str(Path(__file__).resolve().parents[1] / "data" / "personas.csv"))
    parser.add_argument("--salida", default=str(Path(__file__).resolve().parents[1] / "salida" / "templates_example"))
    parser.add_argument("--plantilla", default="certificate.html")
    parser.add_argument("--css", default=str(Path(__file__).resolve().parents[1] / "templates" / "example" / "styles.css"))
    args = parser.parse_args()

    archivo = Path(args.archivo)
    salida_dir = Path(args.salida)
    plantilla_dir = Path(__file__).resolve().parents[1] / "templates" / "example"
    plantilla = args.plantilla
    css_path = Path(args.css)

    if not archivo.exists():
        print(f"No encontré el archivo de datos: {archivo}")
        return

    df = pd.read_csv(archivo)
    if df.empty:
        print("El archivo de datos está vacío.")
        return

    salida_dir.mkdir(parents=True, exist_ok=True)

    archivos_generados = []
    for idx, row in df.iterrows():
        ctx = {k: ("" if pd.isna(v) else v) for k, v in row.items()}
        nombre = ctx.get("Nombre") or ctx.get("nombre") or f"row_{idx}"
        documento = ctx.get("Documento") or ctx.get("Documento") or idx
        filename = f"{safe_name(nombre)}_{safe_name(documento)}.pdf"
        output_path = salida_dir / filename
        try:
            render_dict_to_pdf(ctx, template_dir=plantilla_dir, template_name=plantilla, css_path=css_path, output_path=output_path)
            archivos_generados.append(output_path)
            print(f"Generado: {output_path}")
        except Exception as e:
            print(f"Error al generar {filename}: {e}")

    print(f"Se generaron {len(archivos_generados)} archivos en {salida_dir}")


if __name__ == "__main__":
    main()
