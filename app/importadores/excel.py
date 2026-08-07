import pandas as pd

from app.importadores.comunes import crear_df_filtrado, listar_campos, mostrar_df_campos

__all__ = ["leer_archivo", "listar_campos", "crear_df_filtrado", "mostrar_df_campos"]


def leer_archivo(ruta_archivo, hoja=None):
    df = pd.read_excel(ruta_archivo, sheet_name=hoja or 0)
    return df
