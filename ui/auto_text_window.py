from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QWidget, QInputDialog
from PyQt6.QtCore import Qt
from utils.excel_utils import load_dataframe
from utils.company_utils import get_company_data
from utils.common_functions import show_error_dialog
from config import EXCEL_FILE_PATH, EMAIL_ADDRESS

class AutoTextWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # Referencia a EmailWindow
        self.setWindowTitle("Textos Predefinidos")
        self.setGeometry(150, 150, 600, 400)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Lista de opciones
        self.option_list = QListWidget()
        self.option_list.addItems(["Dar alta S.S.", "Pedir Factura", "Enviar Factura"])
        layout.addWidget(self.option_list)
        
        # Botón de selección
        self.btn_select = QPushButton("Seleccionar")
        self.btn_select.clicked.connect(self.select_option)
        layout.addWidget(self.btn_select)
        
        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def select_option(self):
        selected_option = self.option_list.currentItem().text()
        if not selected_option:
            return
        
        if selected_option == "Dar alta S.S.":
            self._generate_text_alta_ss()
        elif selected_option == "Pedir Factura":
            self._generate_text_pedir_factura()
        elif selected_option == "Enviar Factura":
            self._generate_text_enviar_factura()

    def _generate_text_alta_ss(self):
        subject = "Alta en S.S."
        text = (
            "Hola buenos días\n\n"
            "Querría darme de alta para los días [dias].\n\n"
            "Muchas gracias,\nUn saludo,\nJavier"
        )
        self._apply_text(subject, text)

    def _generate_text_pedir_factura(self):
        # Carga datos de empresas
        try:
            datos_empresa = load_dataframe(EXCEL_FILE_PATH, sheet_name='datos_empresa')
        except Exception as e:
            show_error_dialog(self, "Error", f"Error al cargar datos de empresas: {str(e)}")
            return
        
        company_names = datos_empresa['Nombre_Empresa'].tolist()
        company_name, ok = QInputDialog.getItem(
            self,
            "Seleccionar Empresa",
            "Selecciona la empresa:",
            company_names,
            0,
            False
        )
        if not ok or not company_name:
            return
        
        company_data = get_company_data(company_name, datos_empresa)
        if not company_data:
            show_error_dialog(self, "Error", "No se encontraron datos de la empresa.")
            return
        
        nombre_empresa = company_data.get('Nombre_Empresa', "[Nombre_Empresa]")
        cif = company_data.get('CIF', "[CIF]")
        direccion = company_data.get('Direccion', "[Direccion]")
        
        subject = f"Pedir Factura {nombre_empresa} [Mes]"
        text = (
            f"Hola buenos días\n\n"
            f"Querría hacer una factura de [importe] + IVA,\n"
            f"para el evento [nombre_evento] en [location], como [servicios],\n\n"
            f"Por favor indiquen concepto de referencia en la factura [ref_cliente]\n\n"
            f"Os dejo los datos del cliente:\n"
            f"Nombre: {nombre_empresa}\n"
            f"CIF: {cif}\n"
            f"Dirección: {direccion}\n\n"
            f"Muchas gracias\nUn saludo\nJavier"
        )
        self._apply_text(subject, text)

    def _generate_text_enviar_factura(self):
        # Datos de empresas
        try:
            datos_empresa = load_dataframe(EXCEL_FILE_PATH, sheet_name='datos_empresa')
            datos_cooperativas = load_dataframe(EXCEL_FILE_PATH, sheet_name='datos_cooperativas')
        except Exception as e:
            show_error_dialog(self, "Error", f"Error al cargar datos: {str(e)}")
            return
        
        # Seleccionar empresa
        company_names = datos_empresa['Nombre_Empresa'].tolist()
        company_name, ok = QInputDialog.getItem(
            self,
            "Seleccionar Empresa",
            "Selecciona la empresa:",
            company_names,
            0,
            False
        )
        if not ok or not company_name:
            return
        
        company_data = get_company_data(company_name, datos_empresa)
        if not company_data:
            return
        
        nombre_empresa = company_data.get('Nombre_Empresa', "[Nombre_Empresa]")
        
        # Seleccionar cooperativa
        coop_names = datos_cooperativas['Nombre_Cooperativa'].tolist()
        coop_name, ok = QInputDialog.getItem(
            self,
            "Seleccionar Cooperativa",
            "Selecciona la cooperativa:",
            coop_names,
            0,
            False
        )
        if not ok or not coop_name:
            return
        
        coop_data = get_company_data(coop_name, datos_cooperativas)
        if not coop_data:
            show_error_dialog(self, "Error", "No se encontraron datos de la cooperativa.")
            return
        
        metodos_pago = coop_data.get('Metodo_de_pago', "[Metodos_de_pago]").replace(', ', '\n')
        
        subject = f"Factura {nombre_empresa} [Mes] [ref_cliente]"
        text = (
            f"Hola buenos días\n\n"
            f"Os mando la factura [mes] con un importe total [importe] + IVA,\n"
            f"para el evento [nombre_evento] en [location], como [servicios],\n\n"
            f"Por favor indiquen concepto de referencia en la factura [ref_coop]\n"
            f"Métodos de pago:\n{metodos_pago}\n\n"
            f"Muchas gracias\nUn saludo\nJavier"
        )
        self._apply_text(subject, text)

    def _apply_text(self, subject, text):
        """Enviar datos a la ventana principal y cerrar"""
        if hasattr(self.parent_window, "set_auto_text"):
            self.parent_window.set_auto_text(subject, text)
        else:
            show_error_dialog(self, "Error", "No se puede aplicar el texto predefinido.")
        self.close()