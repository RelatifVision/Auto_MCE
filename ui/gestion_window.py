import os
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget, QTableWidget, QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from utils.gestion_utils import load_gestion_data, create_entry, edit_entry, delete_entry, display_table, save_inline_entry
from utils.common_functions import confirm_action

class GestionWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Gestión de Clientes y Cooperativas")
        self.setGeometry(100, 100, 1920, 1080)
        self.showMaximized()  # [[2]]

        # Crear el layout principal
        layout = QVBoxLayout()

        # --- SECCIÓN EMPRESAS ---
        # Layout principal para empresas (horizontal: tabla a la izquierda, botones a la derecha)
        empresa_layout = QHBoxLayout()

        # Contenedor para la tabla (ocupará el espacio principal)
        table_container_empresa = QWidget()
        table_layout_empresa = QVBoxLayout()
        self.table_empresa = QTableWidget()
        table_layout_empresa.addWidget(self.table_empresa)
        table_container_empresa.setLayout(table_layout_empresa)
        empresa_layout.addWidget(table_container_empresa, stretch=1)  # [[3]]

        # Contenedor para botones (derecha)
        button_container_empresa = QWidget()
        button_layout_empresa = QVBoxLayout()
        self.btn_create = QPushButton("Crear")
        self.btn_edit = QPushButton("Editar")
        self.btn_delete = QPushButton("Borrar")
        self.btn_save_empresa = QPushButton("Guardar")  # Botón sin funcionalidad

        # Estilos comunes
        button_style = """
            QPushButton {
                background-color: rgb(45, 45, 45); color: #ffffff;
                border: 2px solid #000000;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(220, 220, 220); color: #000000;
            }
        """
        for btn in [self.btn_create, self.btn_edit, self.btn_delete, self.btn_save_empresa]:
            btn.setFixedSize(120, 40)
            btn.setStyleSheet(button_style)

        # Conectar botones (solo los que tienen funcionalidad)
        self.btn_create.clicked.connect(lambda: create_entry(self, 'empresa'))
        self.btn_edit.clicked.connect(lambda: edit_entry(self, 'empresa'))
        self.btn_delete.clicked.connect(lambda: delete_entry(self, 'empresa'))
 
        
        # Añadir botones al layout vertical
        button_layout_empresa.addWidget(self.btn_create)
        button_layout_empresa.addWidget(self.btn_edit)
        button_layout_empresa.addWidget(self.btn_delete)
        button_layout_empresa.addWidget(self.btn_save_empresa)
        button_container_empresa.setLayout(button_layout_empresa)
        empresa_layout.addWidget(button_container_empresa, stretch=0)

        # Agregar etiqueta y estructura completa
        empresa_section = QVBoxLayout()
        label_empresa = QLabel("Empresa", alignment=Qt.AlignmentFlag.AlignCenter)
        label_empresa.setStyleSheet("font-weight: bold; font-size: 16px;")
        empresa_section.addWidget(label_empresa)
        empresa_section.addLayout(empresa_layout)
        layout.addLayout(empresa_section)

        # --- SECCIÓN COOPERATIVAS ---
        coop_layout = QHBoxLayout()

        # Contenedor para la tabla
        table_container_coop = QWidget()
        table_layout_coop = QVBoxLayout()
        self.table_coop = QTableWidget()
        table_layout_coop.addWidget(self.table_coop)
        table_container_coop.setLayout(table_layout_coop)
        coop_layout.addWidget(table_container_coop, stretch=1)

        # Contenedor para botones
        button_container_coop = QWidget()
        button_layout_coop = QVBoxLayout()
        self.btn_create_coop = QPushButton("Crear")
        self.btn_edit_coop = QPushButton("Editar")
        self.btn_delete_coop = QPushButton("Borrar")
        self.btn_save_coop = QPushButton("Guardar")  # Botón sin funcionalidad

        for btn in [self.btn_create_coop, self.btn_edit_coop, self.btn_delete_coop, self.btn_save_coop]:
            btn.setFixedSize(120, 40)
            btn.setStyleSheet(button_style)

        # Conectar botones
        self.btn_create_coop.clicked.connect(lambda: create_entry(self, 'cooperativa'))
        self.btn_edit_coop.clicked.connect(lambda: edit_entry(self, 'cooperativa'))
        self.btn_delete_coop.clicked.connect(lambda: delete_entry(self, 'cooperativa'))
        self.btn_save_empresa.clicked.connect(lambda: save_inline_entry(self, 'empresa'))
        self.btn_save_coop.clicked.connect(lambda: save_inline_entry(self, 'cooperativa'))

        # Añadir botones al layout vertical
        button_layout_coop.addWidget(self.btn_create_coop)
        button_layout_coop.addWidget(self.btn_edit_coop)
        button_layout_coop.addWidget(self.btn_delete_coop)
        button_layout_coop.addWidget(self.btn_save_coop)
        button_container_coop.setLayout(button_layout_coop)
        coop_layout.addWidget(button_container_coop, stretch=0)

        # Agregar etiqueta y estructura completa
        coop_section = QVBoxLayout()
        label_coop = QLabel("Cooperativa", alignment=Qt.AlignmentFlag.AlignCenter)
        label_coop.setStyleSheet("font-weight: bold; font-size: 16px;")
        coop_section.addWidget(label_coop)
        coop_section.addLayout(coop_layout)
        layout.addLayout(coop_section)

        # --- BOTONES DE NAVEGACIÓN ---
        
        nav_button_layout = QHBoxLayout()
        self.btn_wpp = QPushButton(" WhatsApp")
        icono_wpp = QIcon(os.path.join("data", "icon", "whatsapp.png"))
        self.btn_wpp.setIcon(icono_wpp)
        self.btn_wpp.setFixedSize(120, 40)
        self.btn_wpp.setStyleSheet(button_style)
        self.btn_wpp.clicked.connect(self.show_main_screen)
        nav_button_layout.addWidget(self.btn_wpp)

        self.btn_calendar = QPushButton(" Calendar")
        icono_calendar = QIcon(os.path.join("data", "icon", "calendar.png"))
        self.btn_calendar.setIcon(icono_calendar)
        self.btn_calendar.setFixedSize(120, 40)
        self.btn_calendar.setStyleSheet(button_style)
        self.btn_calendar.clicked.connect(self.show_calendar)
        nav_button_layout.addWidget(self.btn_calendar)

        self.btn_gmail = QPushButton(" Gmail")
        icono_gmail = QIcon(os.path.join("data", "icon", "gmail.png"))
        self.btn_gmail.setIcon(icono_gmail)
        self.btn_gmail.setFixedSize(120, 40)
        self.btn_gmail.setStyleSheet(button_style)
        self.btn_gmail.clicked.connect(self.show_email)
        nav_button_layout.addWidget(self.btn_gmail)

        self.btn_exit = QPushButton(" Salir")
        icono_exit = QIcon(os.path.join("data", "icon", "exit.png"))
        self.btn_exit.setIcon(icono_exit)
        self.btn_exit.setFixedSize(120, 40)
        self.btn_exit.setStyleSheet(button_style)
        self.btn_exit.clicked.connect(self.close_application)
        nav_button_layout.addWidget(self.btn_exit)

        layout.addLayout(nav_button_layout)

        # Crear un widget central y establecer el layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Cargar datos al iniciar la aplicación
        load_gestion_data(self)  
        self.display_data()      

    def display_data(self):
        """
        Mostrar los datos en las tablas.
        """
        display_table(self.table_empresa, self.df_empresa)
        display_table(self.table_coop, self.df_cooperativa)
    
    # __Funciones de navegación__    
    def show_main_screen(self):
        self.main_window.show_main_screen()

    def show_email(self):
        self.main_window.show_email()
        
    def show_calendar(self):
        self.main_window.show_calendar()
        
    def close_application(self):
        reply = confirm_action(self, "Confirmar salida", "¿Está seguro que desea apagar la aplicación?")
        if reply == QMessageBox.StandardButton.Ok:
            QApplication.instance().quit()  