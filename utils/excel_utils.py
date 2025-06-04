import pandas as pd

def load_dataframe(file_path, sheet_name):
    """
    Cargar un DataFrame desde un archivo Excel.
    :param file_path: Ruta al archivo Excel.
    :param sheet_name: Nombre de la hoja en el archivo Excel.
    :return: DataFrame cargado.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except Exception as e:
        print(f"Error al cargar datos desde el archivo Excel: {e}")
        return pd.DataFrame()

def save_dataframe(df, file_path, sheet_name):
    """
    Guardar un DataFrame en un archivo Excel.
    :param df: DataFrame a guardar.
    :param file_path: Ruta al archivo Excel.
    :param sheet_name: Nombre de la hoja en el archivo Excel.
    """
    try:
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Datos guardados correctamente en {sheet_name}.")
    except Exception as e:
        print(f"Error al guardar datos en el archivo Excel: {e}")

def append_to_dataframe(df, new_entry, file_path, sheet_name):
    """
    Agregar una nueva entrada al DataFrame y guardar los cambios en el archivo Excel.
    :param df: DataFrame actual.
    :param new_entry: Nueva entrada a agregar.
    :param file_path: Ruta al archivo Excel.
    :param sheet_name: Nombre de la hoja en el archivo Excel.
    """
    try:
        df = df._append(new_entry, ignore_index=True)
        save_dataframe(df, file_path, sheet_name)
    except Exception as e:
        print(f"Error al agregar nueva entrada al DataFrame: {e}")

def update_dataframe(df, row_index, updated_entry, file_path, sheet_name):
    """
    Actualizar una fila específica en el DataFrame y guardar los cambios en el archivo Excel.
    :param df: DataFrame actual.
    :param row_index: Índice de la fila a actualizar.
    :param updated_entry: Datos actualizados para la fila.
    :param file_path: Ruta al archivo Excel.
    :param sheet_name: Nombre de la hoja en el archivo Excel.
    """
    try:
        for key, value in updated_entry.items():
            df.at[row_index, key] = value
        save_dataframe(df, file_path, sheet_name)
    except Exception as e:
        print(f"Error al actualizar la fila en el DataFrame: {e}")

def delete_from_dataframe(df, row_index, file_path, sheet_name):
    """
    Eliminar una fila específica del DataFrame y guardar los cambios en el archivo Excel.
    :param df: DataFrame actual.
    :param row_index: Índice de la fila a eliminar.
    :param file_path: Ruta al archivo Excel.
    :param sheet_name: Nombre de la hoja en el archivo Excel.
    """
    try:
        df.drop(index=row_index, inplace=True)
        df.reset_index(drop=True, inplace=True)  # Reiniciar índices
        save_dataframe(df, file_path, sheet_name)
    except Exception as e:
        print(f"Error al eliminar la fila del DataFrame: {e}")
