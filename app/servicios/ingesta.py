from pathlib import Path

from app.importadores import csv as importador_csv
from app.importadores import excel as importador_excel
from app.importadores import ods as importador_ods

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


def cargar_datos(ruta_archivo, hoja=None):
    importador = elegir_importador(ruta_archivo)

    if hoja and importador is importador_csv:
        raise ValueError("La opcion '--hoja' no aplica a archivos CSV.")

    return importador.leer_archivo(ruta_archivo, hoja=hoja)
