# ui/calendar_window.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCalendarWidget, QMainWindow, QApplication, QMessageBox
from PyQt6.QtGui import QIcon, QColor, QFont, QTextCharFormat
from PyQt6.QtCore import Qt, QDate, QTime
import os
from utils.calendar_utils import display_event_info, save_edited_event, delete_event, refresh_calendar, load_calendar_data, create_event, edit_event, show_company_stats, show_company_stats_month, select_date
from utils.common_functions import show_error_dialog, show_info_dialog, confirm_action, close_application
from utils.custom_calendar_utils import CustomCalendar
from utils.dialog_utils import load_company_options

from utils.gui_utils import create_button
from config import EXCEL_FILE_PATH, TASK_OPTIONS, ICON_DIR

class CalendarWindow(QMainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Calendario")
        self.setGeometry(100, 100, 800, 600)
        
        # Usar CustomCalendar
        self.calendar = CustomCalendar()
        
        self.calendar.setStyleSheet(
            """
            QCalendarWidget {
                background-color: #1b376d;  /* Fondo principal */
            }
            QCalendarWidget QHeaderView {
                background-color: #444444;  /* gris claro para días de la semana */
                color: white;
                font-weight: bold;
            }
            QCalendarWidget QToolButton {
                background-color: #444444;
                color: white;
            }
            QCalendarWidget QAbstractItemView {
                background-color: #333333;  /* Fondo gris oscuro por defecto */
                selection-background-color: transparent;  /* Eliminar color de selección fijo */
            }
            QCalendarWidget QTableView::item {
                border: none;  /* Eliminar bordes */
            }
            """
        )
           
        # Configuración básica
        self.calendar.setMinimumDate(QDate(2024, 12, 31))
        self.calendar.setMaximumDate(QDate(2030, 12, 31))
        # Primer día lunes
        self.calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        # Mostrar barra de navegación
        self.calendar.setNavigationBarVisible(True)
        # Mostrar cuadrícula
        self.calendar.setGridVisible(True)  
        # Ocultar encabezado vertical
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)  
        
        # Layout principal
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #1b376d;")
        layout = QVBoxLayout()
        
        # Título y botón Refresh
        title_layout = QHBoxLayout()
        title_label = QLabel("Calendario", alignment=Qt.AlignmentFlag.AlignLeft)
        title_label.setStyleSheet("font-size: 20px; color: #ffffff;")
        title_layout.addWidget(title_label)
        
        self.btn_refresh = QPushButton(" Refresh")
        icono_refresh = QIcon(os.path.join(ICON_DIR, "refresh.png"))
        self.btn_refresh.setIcon(icono_refresh)
        self.btn_refresh.setStyleSheet("background-color: #333333; color: white;")
        self.btn_refresh.setFixedSize(80, 40)
        self.btn_refresh.clicked.connect(lambda: refresh_calendar(self))
        title_layout.addWidget(self.btn_refresh, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(title_layout)
        
        # Añadir el calendario al layout
        layout.addWidget(self.calendar)
        
        # Resaltar el día actual con el formato especificado
        today = QDate.currentDate()
        today_format = QTextCharFormat()
        today_format.setBackground(QColor("#465068"))  # Fondo azul claro
        today_format.setForeground(QColor("black"))    # Texto negro
        self.calendar.setDateTextFormat(today, today_format)
        
        # Mes visible
        self.current_month = QDate.currentDate().toString("yyyy-MM") 
        self.calendar.currentPageChanged.connect(self.update_current_month)
        
        # Conexiones de señales
        self.calendar.clicked.connect(lambda date: select_date(self, date))  
        self.calendar.activated.connect(lambda date: display_event_info(self, date))  
        self.calendar.setMinimumDate(QDate(2024, 12, 31))
        self.calendar.setMaximumDate(QDate(2030, 12, 31))
        
                
        # Botones de acción (Crear/Editar/Borrar/Estadísticas)
        button_layout = QHBoxLayout()
        self.btn_create = QPushButton(" Crear Evento")
        icono_create = QIcon(os.path.join(ICON_DIR, "create.png"))
        self.btn_create.setIcon(icono_create)
        self.btn_create.setStyleSheet("background-color: #333333; color: white;")
        self.btn_create.setFixedSize(120, 40)
        self.btn_create.clicked.connect(lambda: create_event(self))
        button_layout.addWidget(self.btn_create)
        
        self.btn_edit = QPushButton(" Editar Evento")
        icono_edit = QIcon(os.path.join(ICON_DIR, "edit.png"))
        self.btn_edit.setIcon(icono_edit)
        self.btn_edit.setStyleSheet("background-color: #333333; color: white;")
        self.btn_edit.setFixedSize(120, 40)
        self.btn_edit.clicked.connect(lambda: edit_event(self))
        button_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton(" Borrar Evento")
        icono_delete = QIcon(os.path.join(ICON_DIR, "papelera.png"))
        self.btn_delete.setIcon(icono_delete)
        self.btn_delete.setStyleSheet("background-color: #333333; color: white;")
        self.btn_delete.setFixedSize(120, 40)
        self.btn_delete.clicked.connect(lambda: delete_event(self))
        button_layout.addWidget(self.btn_delete)
        
        self.btn_stats = QPushButton(" Estadísticas")
        icono_stats = QIcon(os.path.join(ICON_DIR, "stats.png"))
        self.btn_stats.setIcon(icono_stats)
        self.btn_stats.setStyleSheet("background-color: #333333; color: white;")
        self.btn_stats.setFixedSize(120, 40) 
        self.btn_stats.clicked.connect(self.show_company_stats)
        button_layout.addWidget(self.btn_stats)
        
        layout.addLayout(button_layout)
        
        # Botones de navegación (WhatsApp/Gmail/Salir)
        nav_button_layout = QHBoxLayout()
        self.btn_wpp = QPushButton(" WhatsApp")
        icono_wpp = QIcon(os.path.join(ICON_DIR, "whatsapp.png"))
        self.btn_wpp.setIcon(icono_wpp)
        self.btn_wpp.setFixedSize(120, 40)
        self.btn_wpp.setStyleSheet("background-color: #333333; color: white;")
        self.btn_wpp.clicked.connect(self.show_main_screen)
        nav_button_layout.addWidget(self.btn_wpp)
        
        self.btn_gmail = QPushButton(" Gmail")
        icono_gmail = QIcon(os.path.join(ICON_DIR, "gmail.png"))
        self.btn_gmail.setIcon(icono_gmail)
        self.btn_gmail.setFixedSize(120, 40)
        self.btn_gmail.setStyleSheet("background-color: #333333; color: white;")
        self.btn_gmail.clicked.connect(self.show_email)
        nav_button_layout.addWidget(self.btn_gmail)
        
        self.btn_exit = QPushButton(" Apagar")
        icono_exit = QIcon(os.path.join(ICON_DIR, "off.png"))
        self.btn_exit.setIcon(icono_exit)
        self.btn_exit.setFixedSize(120, 40)
        self.btn_exit.setStyleSheet("background-color: #333333; color: white;")
        self.btn_exit.clicked.connect(self.close_application)
        nav_button_layout.addWidget(self.btn_exit)
        
        layout.addLayout(nav_button_layout)
        
        # Configuración final
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        refresh_calendar(self)
        
    def update_current_month(self, year, month):
        """Actualizar el mes visible cuando el usuario navega."""
        self.current_month = f"{year}-{month:02d}"  # <<<< GUARDAR COMO 'YYYY-MM'

    def show_company_stats(self):
        """Mostrar estadísticas de horas/días por empresa y tarea."""
        try:
            show_company_stats_month(self, self.current_month)
        except Exception as e:
            show_error_dialog(self, "Error", f"Error al calcular: {e}")
    
    def show_main_screen(self):
            self.main_window.show()
    
    def show_email(self):
        self.main_window.show_email()
    
    def show_gestion(self):
        self.main_window.show_gestion()
    
    def close_application(self):
        reply = confirm_action(self, "Confirmar salida", "¿Está seguro que desea apagar la aplicación?")
        if reply == QMessageBox.StandardButton.Ok:
            QApplication.instance().quit() 
