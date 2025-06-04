# ui/email_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QWidget, QLineEdit, QMessageBox, QListWidget
)
from PyQt6.QtWidgets import QInputDialog, QApplication
from PyQt6.QtCore import Qt
from ui.auto_text_window import AutoTextWindow 
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import os
import sys
import base64
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from email.header import decode_header
import pandas as pd
from utils.common_functions import show_error_dialog, show_warning_dialog, show_info_dialog, confirm_action
from utils.company_utils import get_company_data
from utils.dialog_utils import load_company_options
from utils.excel_utils import load_dataframe
from utils.gui_utils import create_button
from utils.file_utils import select_files
from utils.mail_utils import clear_mail_message, load_inbox, load_drafts, get_mail_connection
from config import EMAIL_ADDRESS, APP_PASSWORD, SMTP_SERVER, SMTP_PORT, IMAP_SERVER, IMAP_PORT, EXCEL_FILE_PATH

IMAP_SERVER = "imap.gmail.com"
# Configuración de Gmail IMAP
IMAP_SERVER = "imap.gmail.com"

class EmailWindow(QMainWindow):    
    def __init__(self, main_window):
            super().__init__()
            self.main_window = main_window
            self.attached_files = []
            self.setWindowTitle("Gestión Email")
            self.setGeometry(100, 100, 800, 800)
            self.mail = get_mail_connection()
            
            # Widgets
            self.received_messages_area = QTextEdit()
            self.received_messages_area.setStyleSheet("background-color: #333333;")
            self.subject_input = QLineEdit()
            self.subject_input.setStyleSheet("background-color: #333333;")
            self.destination_input = QLineEdit()
            self.destination_input.setStyleSheet("background-color: #333333;")
            self.compose_area = QTextEdit()
            self.compose_area.setStyleSheet("background-color: #333333;")
            self.attach_list = QListWidget()
            self.attach_list.setStyleSheet("""
            QListWidget {background-color: #333; color: white; border: 1px solid #555;}
            QListWidget::item {padding: 5px;}""")
            self.attach_list.setFixedHeight(self.subject_input.sizeHint().height() * 2)  # Altura de dos líneas de texto
        
            # Configuración de widgets
            self.received_messages_area.setReadOnly(True)
            self.received_messages_area.setPlaceholderText("Aquí aparecerán los mensajes recibidos...")
            
            self.subject_input.setPlaceholderText("Asunto")
            self.destination_input.setPlaceholderText("Destinatario")
            self.compose_area.setPlaceholderText("Escribe tu mensaje aquí...")
            
            # Estilos
            self.setStyleSheet("background-color: #212121;")
            button_style = """
                QPushButton {
                    background-color: rgb(45, 45, 45); 
                    color: white; 
                    border: 2px solid #111111;
                    border-radius: 5px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: rgb(220, 220, 220); 
                    color: black;
                }
            """

            # Layout principal (vertical)
            main_layout = QVBoxLayout()
            
            # --- SECCIÓN DE MENSAJES RECIBIDOS ---
            received_layout = QVBoxLayout()
            received_label = QLabel("Emails recibidos", alignment=Qt.AlignmentFlag.AlignCenter)
            received_label.setStyleSheet("font-size: 20px; color: #ffffff;")
            received_layout.addWidget(received_label)
            received_layout.addWidget(self.received_messages_area)
            main_layout.addLayout(received_layout)
            
            # --- SECCIÓN DE ESCRITURA DE EMAIL ---
            compose_container = QWidget()
            compose_layout = QHBoxLayout()
            
            # Layout izquierdo (campos de texto)
            left_layout = QVBoxLayout()  
            email_label = QLabel("Escribir email", alignment=Qt.AlignmentFlag.AlignCenter)
            email_label.setStyleSheet("font-size: 20px; color: #ffffff;")
            left_layout.addWidget(email_label)
            left_layout.addWidget(self.subject_input)
            left_layout.addWidget(self.destination_input)
            left_layout.addWidget(self.compose_area)
            
            # Agregar la etiqueta de adjuntos y la lista
            left_layout.addWidget(QLabel("Archivos adjuntos:"))
            left_layout.addWidget(self.attach_list)
            
            # Layout derecho (botones de acción)
            action_buttons_layout = QVBoxLayout()
            action_buttons_layout.setSpacing(5)
            
            # __ BOTONES DE ACCIÓN __
            
            action_buttons_layout.addWidget(create_button(
                " Enviar",
                "send_message.png",
                self.send_email
            ))
            
            action_buttons_layout.addWidget(create_button(
                " Adjuntar",
                "adjuntar.png",
                lambda: select_files(self, ["All"], self.attach_list)
            ))
            
            action_buttons_layout.addWidget(create_button(
                " Borrar",
                "papelera.png",
                    lambda: clear_mail_message(
                        self.subject_input, 
                        self.destination_input, 
                        self.compose_area, 
                        self.attach_list
                    )
                ))
                            
            action_buttons_layout.addWidget(create_button(
                " Guardar",
                "draft.png",
                self.save_email
            ))
            
            compose_layout.addLayout(left_layout)
            compose_layout.addLayout(action_buttons_layout)
            compose_container.setLayout(compose_layout)
            main_layout.addWidget(compose_container)
            
            # --- SECCIÓN DE BOTONES ADICIONALES ---
            additional_buttons_layout = QHBoxLayout()
            additional_buttons_layout.addWidget(create_button(
                " Borradores",
                "drafts_view.png",
                self.load_drafts
            ))
            additional_buttons_layout.addWidget(create_button(
                " Recibidos",
                "email_receive.png",
                self.load_received_messages
            ))
            additional_buttons_layout.addWidget(create_button(
                " Autotext",
                "autotext.png",
                self.open_autotext_window
            ))
            main_layout.addLayout(additional_buttons_layout)  
            
            # --- SECCIÓN DE NAVEGACIÓN ---
            nav_buttons_layout = QHBoxLayout()
            nav_buttons_layout.addWidget(create_button(
                " WhatsApp",
                "whatsapp.png",
                self.show_main_screen
            ))
            nav_buttons_layout.addWidget(create_button(
                " Calendar",
                "calendar.png",
                self.show_calendar
            ))
            nav_buttons_layout.addWidget(create_button(
                " Gestión",
                "gestion.png",
                self.show_gestion
            ))
            nav_buttons_layout.addWidget(create_button(
                " Apagar",
                "off.png",
                self.close_application
            ))
            main_layout.addLayout(nav_buttons_layout)

            # Widget central
            central_widget = QWidget()
            central_widget.setLayout(main_layout)
            self.setCentralWidget(central_widget)
            
            # Cargar datos iniciales
            self.load_received_messages()

    def send_email(self):
        """
        Envía el correo electrónico a través de la API de Gmail.
        """
        asunto = self.subject_input.text()
        destination = self.destination_input.text()
        message_text = self.compose_area.toPlainText()

        if not asunto or not destination or not message_text:
            show_warning_dialog(self, "Advertencia", "Todos los campos (Asunto, Destinatario y Mensaje) deben estar llenos.")
            return

        # Crear el mensaje MIME
        message = MIMEMultipart()
        message['Subject'] = asunto
        message['From'] = EMAIL_ADDRESS
        message['To'] = destination
        message.attach(MIMEText(message_text, "plain"))

        try:
            # Conectar al servidor SMTP y enviar el correo
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(EMAIL_ADDRESS, APP_PASSWORD)
                server.sendmail(EMAIL_ADDRESS, destination, message.as_string())
                print("Correo enviado exitosamente.")
                show_info_dialog(self, "Éxito", "Correo enviado exitosamente.")
        except Exception as e:
            print(f"Error al enviar el correo: {e}")
            show_error_dialog(self, "Error", f"Error al enviar el correo: {e}")

    def save_email(self):
        """
        Guardar el correo electrónico en borradores de Gmail.
        """
        asunto = self.subject_input.text()
        destination = self.destination_input.text()
        message_text = self.compose_area.toPlainText()

        if not asunto or not destination or not message_text:
            show_warning_dialog(self, "Advertencia", "Todos los campos (Asunto, Destinatario y Mensaje) deben estar llenos.")
            return

        # Crear el mensaje MIME
        message = MIMEMultipart()
        message['Subject'] = asunto
        message['From'] = EMAIL_ADDRESS
        message['To'] = destination
        message.attach(MIMEText(message_text, "plain"))

        # Convertir el mensaje a base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Cargar las credenciales
        creds = None
        token_path = os.path.join(os.path.dirname(__file__), 'token.json')
        # Obtener la ruta absoluta al directorio raíz del proyecto
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        credentials_path = os.path.join(project_root, 'calendar_api_setting', 'credentials.json')

        if not os.path.exists(credentials_path):
            show_error_dialog(self, "Error", f"El archivo credentials.json no se encuentra en la ruta: {credentials_path}")
            return

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.readonly'])

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, ['https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.readonly'])
                creds = flow.run_local_server(port=0)

            # Guardar las credenciales para la próxima ejecución
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            # Construir el servicio de Gmail
            service = build('gmail', 'v1', credentials=creds)

            # Crear el borrador
            create_draft_request_body = {
                'message': {
                    'raw': raw_message
                }
            }
            print(f"Creando borrador con asunto: {asunto} para {destination}...\n")
            draft = service.users().drafts().create(userId='me', body=create_draft_request_body).execute()

            print(f"Borrador guardado con ID: {draft['id']}")
            show_info_dialog(self, "Éxito", "Correo guardado en borradores correctamente.")
        except HttpError as error:
            print(f"Error al guardar el borrador: {error}")
            show_error_dialog(self, "Error", f"Error al guardar el borrador: {error}")
        except Exception as e:
            print(f"Error inesperado: {e}")
            show_error_dialog(self, "Error", f"Error inesperado: {e}")

    def load_received_messages(self):
        inbox_messages = load_inbox(self.mail, LIMIT=5)
        self.received_messages_area.setPlainText("\n\n".join(inbox_messages))

    def load_drafts(self):
        draft_messages = load_drafts(self.mail, LIMIT=10)
        self.received_messages_area.setPlainText("\n\n".join(draft_messages))
    
    def return_mail(self, mail_ids):
        messages = []
        for num in mail_ids:
            # Obtener el contenido del correo
            status, msg_data = self.mail.fetch(num, "(RFC822)")

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Decodificar el mensaje
                    msg = email.message_from_bytes(response_part[1])

                    # Obtener el asunto
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    # Obtener el remitente
                    from_email = msg.get("From")
                    messages.append(f"De: {from_email}\nAsunto: {subject}\n")
        return messages

    # __AutoText Window__ 
    def open_autotext_window(self):
        """
        Abrir la ventana de textos predefinidos.
        """
        self.auto_text_window = AutoTextWindow(parent=self)
        self.auto_text_window.show()

    def set_auto_text(self, subject, text):
        """Actualizar campos con los valores recibidos"""
        self.subject_input.setText(subject)
        self.destination_input.setText(EMAIL_ADDRESS)
        self.compose_area.setPlainText(text)
    
    # Botones navegación
    def show_main_screen(self):
        self.main_window.show()

    def show_calendar(self):
        self.main_window.show_calendar()

    def show_gestion(self):
        self.main_window.show_gestion()
    
    def close_application(self):
        reply = confirm_action(self, "Confirmar salida", "¿Está seguro que desea apagar la aplicación?")
        if reply == QMessageBox.StandardButton.Ok:
            QApplication.instance().quit()
