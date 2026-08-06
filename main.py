import argparse
from pathlib import Path

from app.generadores.pdf import generar_pdfs
from app.importadores import csv as importador_csv
from app.importadores import excel as importador_excel
from app.importadores import ods as importador_ods
from app.importadores.comunes import crear_df_filtrado, listar_campos

PROYECTO = Path(__file__).resolve().parent
DEFAULT_DATOS = PROYECTO / "data" / "personas.csv"
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


def mostrar_info(df):
    print("Columnas:", ", ".join(listar_campos(df)))
    print(f"Cantidad de registros: {len(df)}")
    print("\nVista previa (primeras 5 filas):")
    print(df.head().to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description="Generador de documentos PDF a partir de datos")
    parser.add_argument(
        "--archivo",
        default=str(DEFAULT_DATOS),
        help="Ruta al archivo de origen (.xlsx, .xls, .csv o .ods)",
    )
    parser.add_argument(
        "--columna",
        default="Estado",
        help="Columna por la que filtrar",
    )
    parser.add_argument(
        "--valor",
        default="Aprobado",
        help="Valor a filtrar en la columna",
    )
    parser.add_argument(
        "--hoja",
        default=None,
        help="Nombre de la hoja a leer (solo .xlsx y .ods)",
    )
    parser.add_argument(
        "--salida",
        default=str(DEFAULT_SALIDA),
        help="Carpeta donde se guardan los documentos",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Mostrar información del archivo y salir",
    )
    args = parser.parse_args()

    try:
        importador = elegir_importador(args.archivo)
    except ValueError as error:
        print(error)
        return

    if args.hoja and importador is importador_csv:
        print("La opcion '--hoja' no aplica a archivos CSV.")
        return

    try:
        df = importador.leer_archivo(args.archivo, hoja=args.hoja)
    except (ValueError, FileNotFoundError) as error:
        print(error)
        return

    if args.info:
        mostrar_info(df)
        return

    try:
        df_filtrado = crear_df_filtrado(df, args.columna, args.valor)
    except ValueError as error:
        print(error)
        print("Columnas disponibles:", ", ".join(listar_campos(df)))
        return

    if df_filtrado.empty:
        print(
            f"No hay registros con '{args.columna}' = '{args.valor}' "
            f"en '{args.archivo}'."
        )
        return

    archivos = generar_pdfs(df_filtrado, args.salida)

    print(f"Se generaron {len(archivos)} documentos en '{args.salida}':")
    for archivo in archivos:
        print(f"  - {archivo.name}")


if __name__ == "__main__":
    main()
