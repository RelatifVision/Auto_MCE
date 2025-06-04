from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QComboBox, QHBoxLayout
from PyQt6.QtCore import Qt
from utils.excel_utils import load_dataframe

def create_dialog(parent, title, fields, buttons):
    dialog = QDialog(parent)
    form_layout = QFormLayout(dialog)

    inputs = {}
    for label, input_type, options in fields:
        if input_type == 'QLineEdit':
            input_field = QLineEdit(dialog)
        elif input_type == 'QComboBox':
            input_field = QComboBox(dialog)
            input_field.addItems(options)
        else:
            continue
        form_layout.addRow(label, input_field)
        inputs[label] = input_field

    button_layout = QHBoxLayout()
    for btn_text, btn_func in buttons:
        btn = QPushButton(btn_text, dialog)
        btn.clicked.connect(btn_func)
        button_layout.addWidget(btn)

    form_layout.addRow("", button_layout)
    dialog.setLayout(form_layout)
    dialog.setWindowTitle(title)
    dialog.exec()
    return inputs

# def get_company_data(company_name, sheet):
#     company_data = sheet[sheet['Nombre_Empresa'] == company_name]
#     if not company_data.empty:
#         return company_data.iloc[0]
#     return None

def get_coop_data(coop_name, sheet):
    coop_data = sheet[sheet['Nombre_Cooperativa'] == coop_name]
    if not coop_data.empty:
        return coop_data.iloc[0]
    return None

def load_company_options(file_path, sheet_name):
    try:
        df = load_dataframe(file_path, sheet_name)
        if 'Nombre_Empresa' not in df.columns:
            raise KeyError("La columna 'Nombre_Empresa' debe existir en la hoja 'datos_empresa'")
        return df['Nombre_Empresa'].tolist()
    except Exception as e:
        print(f"Error al cargar datos de la empresa: {e}")
        return []

def load_coop_options(file_path, sheet_name):
    try:
        df = load_dataframe(file_path, sheet_name)
        if 'Nombre_Cooperativa' not in df.columns:
            raise KeyError("La columna 'Nombre_Cooperativa' debe existir en la hoja 'datos_cooperativas'")
        return df['Nombre_Cooperativa'].tolist()
    except Exception as e:
        print(f"Error al cargar datos de la cooperativa: {e}")
        return []