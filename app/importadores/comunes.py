def listar_campos(df):
    return df.columns.tolist()


def crear_df_filtrado(df, columna, valor):
    if columna not in df.columns:
        raise ValueError(f"La columna '{columna}' no existe en el DataFrame.")
    valores_columna = df[columna].astype(str).str.strip()
    df_filtrado = df[valores_columna == str(valor).strip()]
    return df_filtrado


def mostrar_df_campos(df, columnas):
    if not set(columnas).issubset(df.columns):
        raise ValueError("Algunas columnas no existen en el DataFrame.")
    return df[columnas]
