# utils/company_utils.py
import pandas as pd
from PyQt6.QtGui import QColor
from utils.excel_utils import load_dataframe
from config import EXCEL_FILE_PATH
from utils.common_functions import show_error_dialog  

def get_coop_data(coop_name, df_coops):
    """Obtener datos de una cooperativa desde su DataFrame."""
    try:
        row = df_coops[df_coops['Nombre_Cooperativa'] == coop_name].iloc[0]
        return row.to_dict()
    except:
        return {
            'Nombre_Cooperativa': "[Nombre_Cooperativa]",
            'Metodo_de_pago': "[Metodos_de_pago]",
            'Email': row.get('Mails', "[Mails]")
        }

#___COMPANY_UTILS___
def get_company_data(company_name, df_comp):
    try:
        if df_comp is None:
            return {'Color': '#000000'}  # Color negro por defecto
        
        row = df_comp[df_comp['Nombre_Empresa'] == company_name].iloc[0]
        return row.to_dict()
    except IndexError:
        return {'Color': '#000000'}  # Si la empresa no existe, color negro

def get_company_name(event):
    """Obtener el nombre de la empresa desde la descripción del evento."""
    description = event.get('description', '')
    if not description:
        return "Empresa desconocida"
    
    # Separar tarifa y empresa usando '€' como delimitador
    parts = description.split('€')
    if len(parts) < 2:
        return "Empresa desconocida"  # Si no hay suficientes partes
    
    company_name = parts[1].strip()  # La empresa está después de '€'
    return company_name

def get_company_color(company_name):
    try:
        df_comp = load_dataframe(EXCEL_FILE_PATH, sheet_name='datos_empresa')
        company_colors = dict(zip(df_comp['Nombre_Empresa'], df_comp['Color']))
        return company_colors.get(company_name, "#333333")  
    except Exception as e:
        print(f"Error al cargar datos de la empresa: {e}")
        return "#222222"  # Color por defecto si hay error

def update_company_color(self):
    try:
        df_empresa = load_dataframe(EXCEL_FILE_PATH, sheet_name='datos_empresa')
        selected_company = self.company_input.currentText()
        color_hex = df_empresa.loc[df_empresa['Nombre_Empresa'] == selected_company, 'Color'].values[0]
        self.company_color = QColor(color_hex)  # <<--- Convierte a QColor
        print(f"Color de la empresa {selected_company}: {color_hex}")  # Depuración
    except Exception as e:
        show_error_dialog(self, "Error", f"Error al actualizar el color de la empresa: {e}")

def get_task(event):
    """Obtener la tarea desde extendedProperties."""
    return event.get('extendedProperties', {}).get('private', {}).get('task', 'Sin tarea')

def get_rate_company(description):
    """Obtener la tarifa y el nombre de la empresa desde la descripción del evento."""
    parts = description.split('€')
    if len(parts) != 2:
        return None, None
    rate = parts[0].strip()
    company = parts[1].strip()
    return rate, company