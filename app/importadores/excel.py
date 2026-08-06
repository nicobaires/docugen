import pandas as pd


def leer_archivo(ruta_archivo):
    df = pd.read_excel(ruta_archivo)
    return df


def listar_campos(df):
    return df.columns.tolist()


def crear_df_filtrado(df, columna, valor):
    if columna not in df.columns:
        raise ValueError(f"La columna '{columna}' no existe en el DataFrame.")
    df_filtrado = df[df[columna] == valor]
    return df_filtrado


def mostrar_df_campos(df, columnas):
    if not set(columnas).issubset(df.columns):
        raise ValueError("Algunas columnas no existen en el DataFrame.")
    return df[columnas]
