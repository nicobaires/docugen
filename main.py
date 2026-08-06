import argparse
from pathlib import Path

from app.generadores.pdf import generar_pdfs
from app.importadores.excel import crear_df_filtrado, leer_archivo

PROYECTO = Path(__file__).resolve().parent
DEFAULT_DATOS = PROYECTO / "data" / "personas.xlsx"
DEFAULT_SALIDA = PROYECTO / "salida"


def main():
    parser = argparse.ArgumentParser(description="Generador de certificados PDF")
    parser.add_argument(
        "--archivo",
        default=str(DEFAULT_DATOS),
        help="Ruta al archivo Excel de origen",
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

    df = leer_archivo(args.archivo)
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
