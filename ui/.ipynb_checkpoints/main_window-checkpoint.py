from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QStackedWidget, QWidget, QCalendarWidget, QMessageBox, QColorDialog, QLineEdit, QFormLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QTextCharFormat, QColor
import json
import os
import utils.custom_calendar_utils as CustomCalendar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Resumen y notificaciones")
        self.setGeometry(100, 100, 800, 600)

        # Contenedor principal de pantallas
        self.stacked_widget = QStackedWidget()

        # Pantalla principal
        self.main_screen = self.create_main_screen()
        self.stacked_widget.addWidget(self.main_screen)

        # Pantalla del calendario
        self.calendar_screen = self.create_calendar_screen()
        self.stacked_widget.addWidget(self.calendar_screen)

        # Mostrar la pantalla inicial
        self.setCentralWidget(self.stacked_widget)
        self.stacked_widget.setCurrentWidget(self.main_screen)

        # Cargar y mostrar datos
        self.load_and_display_data()

    def create_main_screen(self):
        """
        Crear la pantalla principal con el historial de conversaciones y notificaciones.
        """
        screen = QWidget()
        layout = QVBoxLayout()

        # Historial de conversaciones
        layout.addWidget(QLabel("Historial de Conversaciones:", alignment=Qt.Alignment.AlignLeft))
        self.history_area = QTextEdit()
        self.history_area.setReadOnly(True)
        self.history_area.setPlaceholderText("Aquí aparecerá el historial completo de conversaciones...")
        layout.addWidget(self.history_area)

        # Notificaciones recientes
        layout.addWidget(QLabel("Notificaciones Recientes:", alignment=Qt.Alignment.AlignLeft))
        self.notification_area = QTextEdit()
        self.notification_area.setReadOnly(True)
        self.notification_area.setPlaceholderText("Aquí aparecerán las notificaciones pendientes...")
        layout.addWidget(self.notification_area)

        # Botones de acción para notificaciones
        button_layout = QHBoxLayout()
        self.btn_review = QPushButton("Revisar")
        self.btn_confirm = QPushButton("Confirmar")
        self.btn_reject = QPushButton("Rechazar")
        self.btn_edit = QPushButton("Editar")

        # Conectar botones (por ahora solo muestran mensajes en consola)
        self.btn_review.clicked.connect(self.review_action)
        self.btn_confirm.clicked.connect(self.confirm_action)
        self.btn_reject.clicked.connect(self.reject_action)
        self.btn_edit.clicked.connect(self.edit_action)

        # Agregar botones al layout
        button_layout.addWidget(self.btn_review)
        button_layout.addWidget(self.btn_confirm)
        button_layout.addWidget(self.btn_reject)
        button_layout.addWidget(self.btn_edit)
        layout.addLayout(button_layout)

        # Botón para cambiar al calendario
        self.btn_calendar = QPushButton("Ir al Calendario")
        self.btn_calendar.clicked.connect(self.show_calendar)
        layout.addWidget(self.btn_calendar)

        screen.setLayout(layout)
        return screen

    def create_calendar_screen(self):
        """
        Crear la pantalla del calendario para personalizar visualizaciones.
        """
        screen = QWidget()
        layout = QVBoxLayout()

        # Título
        layout.addWidget(QLabel("Calendario - Personalización de Horarios y Tarifas", alignment=Qt.Alignment.AlignCenter))

        # Calendario interactivo
        self.calendar = CustomCalendar()
        self.calendar.clicked.connect(self.display_event_info)  # Conectar selección de fecha
        layout.addWidget(self.calendar)

        # Botón para personalizar eventos
        self.btn_customize = QPushButton("Personalizar Evento")
        self.btn_customize.clicked.connect(self.create_event)
        layout.addWidget(self.btn_customize)

        # Botón para volver a la pantalla principal
        self.btn_back = QPushButton("Volver al Resumen")
        self.btn_back.clicked.connect(self.show_main_screen)
        layout.addWidget(self.btn_back)

        screen.setLayout(layout)
        return screen

    def show_calendar(self):
        """
        Cambiar a la pantalla del calendario.
        """
        self.stacked_widget.setCurrentWidget(self.calendar_screen)

    def show_main_screen(self):
        """
        Volver a la pantalla principal.
        """
        self.stacked_widget.setCurrentWidget(self.main_screen)

    # Funciones placeholder para acciones
    def review_action(self):
        print("Revisar notificación seleccionada.")

    def confirm_action(self):
        print("Confirmar acción pendiente.")

    def reject_action(self):
        print("Rechazar acción pendiente.")

    def edit_action(self):
        print("Editar información de la notificación.")

    def load_and_display_data(self):
        """
        Cargar datos de chats y notificaciones y mostrar en las áreas correspondientes.
        """
        # Cargar chats (suponiendo que tienes la función 'load_chats' en models/chat_parser.py)
        try:
            from models.chat_parser import load_chats
            chats = load_chats()

            # Mostrar historial completo de conversaciones
            if chats:
                history_text = "\n\n".join([f"Conversación - {name}:\n{content}" for name, content in chats.items()])
                self.history_area.setPlainText(history_text)
            else:
                self.history_area.setPlainText("No hay conversaciones disponibles.")
        except ImportError:
            self.history_area.setPlainText("No se pudo cargar el historial de conversaciones.")

        # Cargar notificaciones desde un archivo JSON
        try:
            with open("data/notifications.json", "r", encoding="utf-8") as file:
                notifications = json.load(file)
            notification_text = "\n".join([f"{n['id']}. {n['message']} - {n['date']}" for n in notifications])
            self.notification_area.setPlainText(notification_text)
        except FileNotFoundError:
            self.notification_area.setPlainText("No se encontró el archivo de notificaciones.")
        except json.JSONDecodeError:
            self.notification_area.setPlainText("Error al leer las notificaciones.")

        # Cargar y mostrar los eventos del calendario
        self.load_calendar_events()

    def load_calendar_events(self):
        """
        Cargar y mostrar los eventos en el calendario con colores y tarifas.
        """
        try:
            with open("data/calendar_data.json", "r", encoding="utf-8") as file:
                calendar_data = json.load(file)
            
            for event in calendar_data:
                date = event["date"]
                company = event["company"]
                rate = event["rate"]
                color = event["color"]

                # Formato de texto para marcar la fecha con un color de fondo
                calendar_format = QTextCharFormat()
                calendar_format.setBackground(QColor(color))

                # Convertir la fecha a formato QDate
                year, month, day = map(int, date.split('-'))
                event_date = QDate(year, month, day)

                # Aplicar el formato de color a la fecha seleccionada
                self.calendar.setDateTextFormat(event_date, calendar_format)

        except FileNotFoundError:
            print("No se encontró el archivo de eventos del calendario.")
        except json.JSONDecodeError:
            print("Error al leer los eventos del calendario.")

    def display_event_info(self, date):
        """
        Mostrar la información del evento al hacer clic en una fecha.
        """
        selected_date = date.toString("yyyy-MM-dd")
        events = self.load_calendar_data(selected_date)
        
        if events:
            event_info = "\n".join([f"Empresa: {event['company']}\nHorario: {event['hours']}\nTarifa: {event['rate']}" for event in events])
        else:
            event_info = "No hay eventos para esta fecha."

        QMessageBox.information(self, f"Eventos para {selected_date}", event_info)

    def load_calendar_data(self, selected_date):
        """
        Cargar eventos para una fecha seleccionada.
        """
        try:
            with open("data/calendar_data.json", "r", encoding="utf-8") as file:
                calendar_data = json.load(file)
            events = [event for event in calendar_data if event["date"] == selected_date]
            return events
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def create_event(self):
        """
        Personalizar evento para la fecha seleccionada, incluyendo color, horario y tarifa.
        """
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        print(f"Fecha seleccionada: {selected_date}")  # Depuración
    
        # Selección de color
        color = QColorDialog.getColor()
        if not color.isValid():
            print("Color no válido")
            return
    
        print(f"Color seleccionado: {color.name()}")  # Depuración
    
        # Obtener horario y tarifa
        dialog = QWidget()
        form_layout = QFormLayout(dialog)
    
        self.hour_input = QLineEdit(dialog)
        self.rate_input = QLineEdit(dialog)
    
        form_layout.addRow("Hora del evento:", self.hour_input)
        form_layout.addRow("Tarifa del evento:", self.rate_input)
    
        dialog.setLayout(form_layout)
        dialog.setWindowTitle("Editar Evento")
        dialog.resize(300, 150)
    
        if dialog.exec_():
            hours = self.hour_input.text()
            rate = self.rate_input.text()
    
            print(f"Hora: {hours}, Tarifa: {rate}")  # Depuración
    
            # Actualizar el calendario con el color
            calendar_format = QTextCharFormat()
            calendar_format.setBackground(color)
            self.calendar.setDateTextFormat(self.calendar.selectedDate(), calendar_format)
    
            # Guardar la personalización del evento
            event_data = {
                "date": selected_date,
                "company": "VisualMax S.L.",  # Puedes cambiarlo si es dinámico
                "color": color.name(),
                "hours": hours,
                "rate": rate
            }
    
            # Cargar eventos actuales y agregar el nuevo
            try:
                with open("data/calendar_data.json", "r", encoding="utf-8") as file:
                    calendar_data = json.load(file)
                print(f"Eventos cargados: {calendar_data}")  # Depuración
            except (FileNotFoundError, json.JSONDecodeError):
                print("Archivo no encontrado o error al leer el JSON")
                calendar_data = []
    
            # Buscar si ya existe un evento para la fecha seleccionada
            event_found = False
            for event in calendar_data:
                if event["date"] == selected_date:
                    event.update(event_data)
                    event_found = True
                    break
            
            if not event_found:
                calendar_data.append(event_data)
    
            # Guardar los cambios
            try:
                with open("data/calendar_data.json", "w", encoding="utf-8") as file:
                    json.dump(calendar_data, file, indent=4)
                print("Eventos guardados con éxito.")  # Depuración
            except Exception as e:
                print(f"Error al guardar el archivo: {e}")
    
            QMessageBox.information(self, "Personalización", f"Evento para {selected_date} personalizado con color {color.name()}, hora {hours}, tarifa {rate}.")
            self.load_calendar_events()  # Volver a cargar los eventos del calendario para actualizar la vista

