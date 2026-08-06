import argparse
from pathlib import Path

from app.generadores.pdf import generar_pdfs
from app.importadores import csv as importador_csv
from app.importadores import excel as importador_excel
from app.importadores import ods as importador_ods
from app.importadores.comunes import crear_df_filtrado

PROYECTO = Path(__file__).resolve().parent
DEFAULT_DATOS = PROYECTO / "data" / "personas.xlsx"
DEFAULT_SALIDA = PROYECTO / "salida"

IMPORTADORES = {
    ".xlsx": importador_excel,
    ".xls": importador_excel,
    ".csv": importador_csv,
    ".ods": importador_ods,
}


def elegir_importador(ruta_archivo):
    extension = Path(ruta_archivo).suffix.lower()
    try:
        return IMPORTADORES[extension]
    except KeyError:
        soportadas = ", ".join(sorted(IMPORTADORES))
        raise ValueError(
            f"Formato '{extension}' no soportado. Usar: {soportadas}"
        )


def main():
    parser = argparse.ArgumentParser(description="Generador de certificados PDF")
    parser.add_argument(
        "--archivo",
        default=str(DEFAULT_DATOS),
        help="Ruta al archivo de origen (.xlsx, .xls, .csv o .ods)",
    )
    parser.add_argument(
        "--estado",
        default="Aprobado",
        help="Filtrar los registros por estado",
    )
    parser.add_argument(
        "--salida",
        default=str(DEFAULT_SALIDA),
        help="Carpeta donde se guardan los certificados",
    )
    args = parser.parse_args()

    try:
        importador = elegir_importador(args.archivo)
    except ValueError as error:
        print(error)
        return

    df = importador.leer_archivo(args.archivo)
    df_filtrado = crear_df_filtrado(df, "Estado", args.estado)

    if df_filtrado.empty:
        print(f"No hay registros con estado '{args.estado}' en '{args.archivo}'.")
        return

    archivos = generar_pdfs(df_filtrado, args.salida)

    print(f"Se generaron {len(archivos)} certificados en '{args.salida}':")
    for archivo in archivos:
        print(f"  - {archivo.name}")


if __name__ == "__main__":
    main()
