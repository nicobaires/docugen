import pandas as pd

from app.importadores.comunes import crear_df_filtrado, listar_campos, mostrar_df_campos

__all__ = ["leer_archivo", "listar_campos", "crear_df_filtrado", "mostrar_df_campos"]


def leer_archivo(ruta_archivo):
    df = pd.read_csv(ruta_archivo, sep=None, engine="python")
    return df
