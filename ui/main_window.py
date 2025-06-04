import spacy
import os
import re
import pandas as pd

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QStackedWidget, QWidget, QCalendarWidget, QMessageBox, QColorDialog, QInputDialog, QFormLayout, QLineEdit, QDialog, QComboBox, QApplication, QTimeEdit, QTableWidget, QTableWidgetItem, QListWidget, QStyle
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor, QIcon
from selenium.webdriver.common.by import By

from calendar_api_setting.calendar_api import get_credentials, create_event_api, get_events, get_events_by_month, delete_event_api, edit_event_api, refresh_calendar
from config import EMAIL_ADDRESS, EXCEL_FILE_PATH

from ui.calendar_window import CalendarWindow  
from ui.email_window import EmailWindow 
from ui.gestion_window import GestionWindow

from utils.common_functions import show_error_dialog, show_warning_dialog, show_info_dialog, confirm_action, close_application
from utils.company_utils import update_company_color, get_company_data
from utils.dialog_utils import create_dialog, load_company_options
from utils.excel_utils import load_dataframe
from utils.file_utils import select_files, clear_whatsapp_message 
from utils.gui_utils import create_button
from utils.whatsapp_utils import send_wpp, update_chat_content, confirm_wpp, load_chats, load_and_display_data, reject_wpp
from models.chat_parser import load_chats, is_relevant_message, extract_relevant_messages, nlp
from utils.whatsapp_utils import clear_whatsapp_message


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.email_window = None
        self.calendar_window = None
        self.gestion_window = None
        self.setWindowTitle("Auto_WCM")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #212121;")
        
        # Widgets necesarios para WhatsApp
        self.chat_content = QTextEdit()  
        self.chat_content.setReadOnly(True)
        self.chat_content.setStyleSheet("QTextEdit { background-color: #333333; color: white; }")
        
        # Campo de destinatario
        self.destination_input = QLineEdit()
        self.destination_input.setPlaceholderText("Destinatario seleccionado")
        self.destination_input.setFixedWidth(200) 
        self.destination_input.setStyleSheet("background-color: #333; color: white;")

        # Crear botones usando el helper
        self.btn_confirm = create_button(
            " Confirmar",
            "tick.png",
            lambda: confirm_wpp(self) 
        )
        
        self.btn_reject = create_button(
            " Rechazar",
            "x.png",
            lambda: reject_wpp(self)  
        )
        
        self.btn_email = create_button(
            " Gmail",
            "gmail.png",
            self.show_email
        )
        
        self.btn_calendar = create_button(
            " Calendar",
            "calendar.png",
            self.show_calendar
        )
        
        self.btn_gestion = create_button(
            " Gestión",
            "gestion.png",
            self.show_gestion
        )
        
        self.btn_exit = create_button(
            " Apagar",
            "off.png",
            self.close_application
        )
        self.attach_list = QListWidget()
        self.attach_list.setStyleSheet("""
        QListWidget {background-color: #333; color: white; border: 1px solid #555;}
        QListWidget::item {padding: 5px;}""")
        self.attach_list.setMinimumHeight(10)
        self.attached_files =[]  # Lista para almacenar archivos adjuntos
        # Crear contenedor principal
        self.stacked_widget = QStackedWidget()  
        self.main_screen = self.create_main_screen() 
        self.stacked_widget.addWidget(self.main_screen) 
        self.setCentralWidget(self.stacked_widget)
        
        # Cargar datos una vez
        load_and_display_data(self)

    def create_chat_list(self, on_change_callback):
        chat_list = QListWidget()
        chat_list.setFixedWidth(200)
        chat_list.setStyleSheet("QListWidget { background-color: #333333; color: white; }")
        chat_list.currentItemChanged.connect(
            lambda current, prev: on_change_callback(self, current, chat_list)  
        )
        return chat_list

    def create_send_section(self):
        container = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Enviar What'sApp", alignment=Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; color: #ffffff;")
        layout.addWidget(title_label)
        
        # Layout principal para la sección de envío
        message_layout = QHBoxLayout()
        
        # Lista de chats (izquierda)
        self.chat_list_send = self.create_chat_list(update_chat_content)
        message_layout.addWidget(self.chat_list_send, stretch=1)  # Factor de expansión 1
        
        # Área de mensaje (centro)
        self.message_input = QTextEdit()
        self.message_input.setStyleSheet("QTextEdit { background-color: #333333; color: white; }")
        message_layout.addWidget(self.message_input, stretch=2)  # Factor de expansión 2
        
        # Contenedor para botones (derecha)
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_container.setLayout(buttons_layout)
        message_layout.addWidget(buttons_container, stretch=0)
        
        # Botón Enviar
        btn_send = create_button(
            " Enviar",
            "send_message.png",
            lambda: send_wpp(self),
            fixed_size=(120, 40)
        )
        buttons_layout.addWidget(btn_send)
        
        # Botón Adjuntar
        btn_attach = create_button(
            " Adjuntar",
            "adjuntar.png",
            lambda: select_files(self, ["Images", "Videos", "PDF", "PNG"], self.attach_list),
            fixed_size=(120, 40)
        )
        buttons_layout.addWidget(btn_attach)
        
        # Botón Borrar
        btn_delete = create_button(
            " Borrar",
            "papelera.png",
            lambda: clear_whatsapp_message(
                chat_list=self.chat_list_send,
                compose_area=self.message_input,
                attach_list=self.attach_list
            ),
            fixed_size=(120, 40)
        )
        buttons_layout.addWidget(btn_delete)
        
        message_layout.addLayout(buttons_layout)
        # Añadir el layout principal al contenedor
        layout.addLayout(message_layout)
        
        # Lista de adjuntos debajo del área de mensaje
        self.attach_list.setFixedHeight(40)
        layout.addWidget(self.attach_list)
        
        container.setLayout(layout)
        return container
    
    def create_main_screen(self):
        screen = QWidget()
        screen.setStyleSheet("background-color: #112211;")
        main_layout = QVBoxLayout()

        # Título Historial
        title_label = QLabel("Historial What'sApp", alignment=Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; color: #ffffff;")
        main_layout.addWidget(title_label)

        # Lista de chats superior (historial)
        self.chat_list = self.create_chat_list(update_chat_content)
        chat_layout = QHBoxLayout()
        chat_layout.addWidget(self.chat_list)
        chat_layout.addWidget(self.chat_content)
        main_layout.addLayout(chat_layout)

        # Sección de envío
        send_container = self.create_send_section()
        main_layout.addWidget(send_container)

        # Botones de acción
        button_layout = QVBoxLayout()
        
        # Grupo de confirmar/rechazar
        confirm_reject_layout = QHBoxLayout()
        confirm_reject_layout.addWidget(self.btn_confirm)
        confirm_reject_layout.addWidget(self.btn_reject)
        button_layout.addLayout(confirm_reject_layout)

        # Botones de navegación
        nav_buttons = [
            self.btn_email,
            self.btn_calendar,
            self.btn_gestion,
            self.btn_exit
        ]
        nav_layout = QHBoxLayout()
        for btn in nav_buttons:
            nav_layout.addWidget(btn)
        button_layout.addLayout(nav_layout)

        main_layout.addLayout(button_layout)
        screen.setLayout(main_layout)
        return screen
 
    # __ Funciones de navegación __#
    
    def show_calendar(self):
        if not self.calendar_window:
            self.calendar_window = CalendarWindow(main_window=self) 
        self.calendar_window.show()
    
    def show_email(self):
        """
        Abrir la ventana del cliente de correo electrónico.
        """
        self.email_window = EmailWindow(self)
        self.email_window.show()

    def show_gestion(self):
        """
        Abrir la ventana de gestión.
        """
        self.gestion_window = GestionWindow(self)
        self.gestion_window.show()
        
        # __Mostrar Main__
    
    def show_main_screen(self):
        """
        Volver a la pantalla principal.
        """
        self.stacked_widget.setCurrentWidget(self.main_screen)
    
    def close_application(self):
        reply = confirm_action(self, "Confirmar salida", "¿Está seguro que desea apagar la aplicación?")
        if reply == QMessageBox.StandardButton.Ok:
            QApplication.instance().quit() 

    

