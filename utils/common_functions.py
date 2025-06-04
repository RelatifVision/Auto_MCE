# utils/common_functions.py
import os
from PyQt6.QtWidgets import QMessageBox, QApplication, QInputDialog
from PyQt6.QtGui import QIcon
from config import ICON_DIR


def show_error_dialog(parent, title, message):
    QMessageBox.critical(parent, title, message)

def show_warning_dialog(parent, title, message):
    QMessageBox.warning(parent, title, message)

def show_info_dialog(parent, title, message):
    QMessageBox.information(parent, title, message)

def confirm_action(parent, title, message):
    msg = QMessageBox(parent)  
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    return msg.exec()
      
# Seleccionar empresa/cooperativa
# def get_company_from_user(parent, df_comp):
#     """Seleccionar empresa y obtener datos."""
#     company_names = df_comp['Nombre_Empresa'].tolist()
#     company_name, ok = QInputDialog.getItem(
#         parent,
#         "Empresa",
#         "Seleccione la empresa:",
#         company_names,
#         0,
#         False
#     )
#     if ok and company_name:
#         return get_company_data(company_name, df_comp)
#     else:
#         return None

# def get_coop_from_user(parent, df_coops):
#     """Seleccionar cooperativa y obtener datos."""
#     coop_names = df_coops['Nombre_Cooperativa'].tolist()
#     coop_name, ok = QInputDialog.getItem(
#         parent,
#         "Cooperativa",
#         "Seleccione la cooperativa:",
#         coop_names,
#         0,
#         False
#     )
#     if ok and coop_name:
#         return get_coop_data(coop_name, df_coops)
#     else:
#         return None
    
#__Cerrar aplicación__
def close_application(self):
    reply = confirm_action(self, "Confirmar salida", "¿Está seguro que desea apagar la aplicación?", QIcon(os.path.join(ICON_DIR, "off.png")))
    if reply == QMessageBox.StandardButton.Ok:
        QApplication.instance().quit()