from app.generadores.pdf import generar_pdfs
from app.generadores.plantilla import generar_pdfs_con_plantilla
from app.importadores.comunes import crear_df_filtrado, listar_campos
from app.servicios.configuracion import (
    cargar_configuracion,
    guardar_configuracion,
    restablecer_configuracion,
)
from app.servicios.ingesta import cargar_datos

CAMPOS_CONFIGURABLES = [
    "archivo",
    "columna",
    "valor",
    "hoja",
    "salida",
    "plantilla",
    "css",
]


def mostrar_info(df):
    print("Columnas:", ", ".join(listar_campos(df)))
    print(f"Cantidad de registros: {len(df)}")
    print("\nVista previa (primeras 5 filas):")
    print(df.head().to_string(index=False))


def resolver_valores(args, configuracion):
    return {
        campo: getattr(args, campo) if getattr(args, campo) is not None
        else configuracion.get(campo)
        for campo in CAMPOS_CONFIGURABLES
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generador de documentos PDF a partir de datos")
    parser.add_argument(
        "--archivo",
        default=None,
        help="Ruta al archivo de origen (.xlsx, .xls, .csv o .ods)",
    )
    parser.add_argument(
        "--columna",
        default=None,
        help="Columna por la que filtrar",
    )
    parser.add_argument(
        "--valor",
        default=None,
        help="Valor a filtrar en la columna",
    )
    parser.add_argument(
        "--hoja",
        default=None,
        help="Nombre de la hoja a leer (solo .xlsx y .ods)",
    )
    parser.add_argument(
        "--salida",
        default=None,
        help="Carpeta donde se guardan los documentos",
    )
    parser.add_argument(
        "--plantilla",
        default=None,
        help="Plantilla HTML (Jinja2) para generar los documentos",
    )
    parser.add_argument(
        "--css",
        default=None,
        help="Hoja de estilos CSS para la plantilla (opcional)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Mostrar información del archivo y salir",
    )
    parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Restablecer la configuración guardada",
    )
    args = parser.parse_args()

    if args.reset_config:
        restablecer_configuracion()
        print("Configuración restablecida.")
        return

    configuracion = cargar_configuracion()
    valores = resolver_valores(args, configuracion)

    try:
        df = cargar_datos(valores["archivo"], hoja=valores["hoja"])
    except (ValueError, FileNotFoundError) as error:
        print(error)
        return

    if args.info:
        mostrar_info(df)
        return

    try:
        df_filtrado = crear_df_filtrado(df, valores["columna"], valores["valor"])
    except ValueError as error:
        print(error)
        print("Columnas disponibles:", ", ".join(listar_campos(df)))
        return

    if df_filtrado.empty:
        print(
            f"No hay registros con '{valores['columna']}' = '{valores['valor']}' "
            f"en '{valores['archivo']}'."
        )
        return

    if valores["plantilla"]:
        archivos = generar_pdfs_con_plantilla(
            df_filtrado, valores["plantilla"], valores["salida"], css=valores["css"]
        )
    else:
        archivos = generar_pdfs(df_filtrado, valores["salida"])

    guardar_configuracion(valores)

    print(f"Se generaron {len(archivos)} documentos en '{valores['salida']}':")
    for archivo in archivos:
        print(f"  - {archivo.name}")
