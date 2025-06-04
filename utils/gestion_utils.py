from PyQt6.QtWidgets import QMessageBox, QDialog, QLineEdit, QFormLayout, QPushButton, QTableWidgetItem, QTableWidget
import pandas as pd

def load_gestion_data(window):
    try:
        window.df_empresa = pd.read_excel('data/db.xlsx', sheet_name='datos_empresa')
        window.df_cooperativa = pd.read_excel('data/db.xlsx', sheet_name='datos_cooperativas')
        window.display_data()  # <<<< LLAMADA A display_data DESPUÉS DE CARGAR LOS DATOS
    except Exception as e:
        QMessageBox.critical(window, "Error", f"Error al cargar datos: {e}")

def display_table(table, df):
    """
    Mostrar los datos en una tabla específica.
    """
    table.clear()
    table.setRowCount(0)
    table.setColumnCount(len(df.columns))
    table.setHorizontalHeaderLabels(df.columns)
    table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)
    for i, row in df.iterrows():
        table.insertRow(i)
        for j, value in enumerate(row):
            table.setItem(i, j, QTableWidgetItem(str(value)))
    # Ajustar el tamaño de las columnas para que se muestren completas
    table.resizeColumnsToContents()
    table.resizeRowsToContents()

def create_entry(window, entry_type):
    """
    Crear una nueva entrada en la hoja de datos.
    """
    dialog = QDialog(window)
    form_layout = QFormLayout(dialog)
    inputs = {}
    fields = get_fields(entry_type)
    
    for field in fields:
        inputs[field] = QLineEdit(dialog)
        form_layout.addRow(f"{field.replace('_', ' ').title()}:", inputs[field])
    
    btn_save = QPushButton("Guardar")
    btn_save.clicked.connect(lambda: save_entry(window, dialog, entry_type, inputs))
    form_layout.addWidget(btn_save)
    dialog.setLayout(form_layout)
    dialog.setWindowTitle(f"Crear Entrada {entry_type.title()}")
    dialog.exec()

def save_entry(window, dialog, entry_type, inputs):
    """
    Guardar la nueva entrada en el archivo Excel.
    """
    try:
        new_entry = {field: inputs[field].text() for field in inputs}
        new_entry = validate_entry(new_entry, entry_type)
        if new_entry is None:
            return

        df = pd.read_excel('data/db.xlsx', sheet_name=f'datos_{entry_type}')
        df = df._append(new_entry, ignore_index=True)
        with pd.ExcelWriter('data/db.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=f'datos_{entry_type}', index=False)
        load_gestion_data(window)
        dialog.accept()
    except Exception as e:
        QMessageBox.critical(window, "Error", f"Error al guardar la entrada: {e}")
        dialog.reject()

def edit_entry(window, entry_type):
    """
    Editar la entrada seleccionada en la hoja de datos.
    """
    selected_row = get_selected_row(window, entry_type)
    if selected_row < 0:
        QMessageBox.warning(window, "Advertencia", "Seleccione una fila para editar.")
        return

    dialog = QDialog(window)
    form_layout = QFormLayout(dialog)
    inputs = {}
    fields = get_fields(entry_type)
    
    for i, field in enumerate(fields):
        inputs[field] = QLineEdit(dialog)
        inputs[field].setText(get_item_text(window, entry_type, selected_row, i))
        form_layout.addRow(f"{field.replace('_', ' ').title()}:", inputs[field])
    
    btn_save = QPushButton("Guardar")
    btn_save.clicked.connect(lambda: save_edited_entry(window, dialog, entry_type, selected_row, inputs))
    form_layout.addWidget(btn_save)
    dialog.setLayout(form_layout)
    dialog.setWindowTitle(f"Editar Entrada {entry_type.title()}")
    dialog.exec()

def save_edited_entry(window, dialog, entry_type, selected_row, inputs):
    """
    Guardar los cambios realizados en la entrada seleccionada.
    """
    try:
        updated_entry = {field: inputs[field].text() for field in inputs}
        updated_entry = validate_entry(updated_entry, entry_type)
        if updated_entry is None:
            return

        df = getattr(window, f'df_{entry_type}')
        for field in inputs:
            df.at[selected_row, field] = updated_entry[field]

        with pd.ExcelWriter('data/db.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=f'datos_{entry_type}', index=False)
        load_gestion_data(window)
        dialog.accept()
    except Exception as e:
        QMessageBox.critical(window, "Error", f"Error al guardar los cambios: {e}")
        dialog.reject()

def save_inline_entry(window, entry_type):
    selected_row = get_selected_row(window, entry_type)
    if selected_row < 0:
        QMessageBox.warning(window, "Advertencia", "Seleccione una fila para guardar.")
        return

    try:
        df = getattr(window, f'df_{entry_type}')
        table = window.table_empresa if entry_type == 'empresa' else window.table_coop

        # Actualizar el DataFrame con los valores de la tabla
        for col in range(table.columnCount()):
            item = table.item(selected_row, col)
            if item:
                df.iloc[selected_row, col] = item.text()  # <<<< Actualizar con el valor de la celda

        # Guardar cambios en el archivo Excel
        with pd.ExcelWriter('data/db.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=f'datos_{entry_type}', index=False)
        load_gestion_data(window)  # Recargar datos para reflejar cambios
    except Exception as e:
        QMessageBox.critical(window, "Error", f"Error al guardar: {e}")

def delete_entry(window, entry_type):
    """
    Borrar la entrada seleccionada en la hoja de datos.
    """
    selected_row = get_selected_row(window, entry_type)
    if selected_row < 0:
        QMessageBox.warning(window, "Advertencia", "Seleccione una fila para borrar.")
        return

    confirm = QMessageBox.question(
        window,
        "Confirmar Eliminación",
        "¿Está seguro de que desea eliminar esta entrada?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if confirm != QMessageBox.StandardButton.Yes:
        return

    df = getattr(window, f'df_{entry_type}')
    df.drop(index=selected_row, inplace=True)
    df.reset_index(drop=True, inplace=True)

    with pd.ExcelWriter('data/db.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=f'datos_{entry_type}', index=False)
    load_gestion_data(window)

def get_fields(entry_type):
    """
    Obtener los campos para el tipo de entrada.
    """
    if entry_type == 'empresa':
        return ["ID_Empresa", "Nombre_Empresa", "CIF", "Direccion", "Color", "Email", "Telefono", "Jornada_Precio", "Jornada_Horas", "Precio_Hora"]
    elif entry_type == 'cooperativa':
        return ["ID_Coop", "Nombre_Cooperativa", "Metodo_de_pago", "Mails", "Telefono", "CIF"]
    return []

def validate_entry(entry, entry_type):
    """
    Validar la entrada antes de guardarla.
    """
    if entry_type == 'empresa' and not entry["ID_Empresa"].isdigit():
        QMessageBox.warning(None, "Advertencia", "El ID de la empresa debe ser un número entero.")
        return None
    if entry_type == 'cooperativa' and not entry["ID_Coop"].isdigit():
        QMessageBox.warning(None, "Advertencia", "El ID de la cooperativa debe ser un número entero.")
        return None
    return entry

def get_selected_row(window, entry_type):
    """
    Obtener la fila seleccionada en la tabla correspondiente.
    """
    if entry_type == 'empresa':
        return window.table_empresa.currentRow()
    elif entry_type == 'cooperativa':
        return window.table_coop.currentRow()
    return -1

def get_item_text(window, entry_type, row, column):
    """
    Obtener el texto de un elemento de la tabla, asegurándose de que exista.
    """
    if entry_type == 'empresa':
        item = window.table_empresa.item(row, column)
    elif entry_type == 'cooperativa':
        item = window.table_coop.item(row, column)
    return item.text() if item is not None else ""