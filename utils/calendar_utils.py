# utils/calendar_utils.py
import json
import pandas as pd
from datetime import datetime
from PyQt6.QtCore import QDate, QTime, QDateTime
from PyQt6.QtWidgets import QPushButton, QDialog, QFormLayout, QComboBox, QLineEdit, QTimeEdit, QMessageBox
from PyQt6.QtGui import QIcon, QColor, QTextCharFormat
from calendar_api_setting.calendar_api import create_event_api, get_events, get_events_by_month, delete_event_api, edit_event_api, get_credentials
from utils.common_functions import show_info_dialog, show_error_dialog, confirm_action
from utils.dialog_utils import load_company_options
from utils.excel_utils import load_dataframe
from utils.business_manager import BusinessManager
from utils.company_utils import get_company_name, get_company_color, get_task, get_company_data
from config import EXCEL_FILE_PATH, TASK_OPTIONS

def refresh_calendar(calendar_window):
    try:
        events = get_events()
        events_by_date = {}  # {QDate: [event1, event2, ...]}
        
        for event in events:
            start_date_str = event['start']['dateTime'][:10]
            start_date = QDate.fromString(start_date_str, "yyyy-MM-dd")
            company = get_company_name(event)
            event_data = {
                "company": company,
                "start": event["start"],
                "end": event["end"]
            }
            if start_date not in events_by_date:
                events_by_date[start_date] = []
            events_by_date[start_date].append(event_data)
        
        # Actualizar CustomCalendar
        calendar_window.calendar.set_events_by_date(events_by_date)
        calendar_window.calendar.update()  # Forzar repintado
        
    except Exception as e:
        show_error_dialog(calendar_window, "Error", f"Error al refrescar: {str(e)}")
        
def combine_colors(colors):
    """Combinar colores en un promedio RGB."""
    r_total = 0
    g_total = 0
    b_total = 0
    count = len(colors)

    for color_hex in colors:
        # Convertir color hex a RGB
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
        r_total += r
        g_total += g
        b_total += b

    # Calcular promedio
    avg_r = r_total // count
    avg_g = g_total // count
    avg_b = b_total // count

    # Convertir a formato hex
    return f"#{avg_r:02X}{avg_g:02X}{avg_b:02X}"

def display_event_info(calendar_window, date):
    """Muestra detalles del evento con formato HTML y colores."""
    selected_date = date.toString("yyyy-MM-dd")
    events = load_calendar_data(calendar_window, selected_date)
    if not events:
        show_info_dialog(calendar_window, "Detalles", "No hay eventos para esta fecha.")
        return
    formatted_events = []
    for event in events:
        company = get_company_name(event)
        task = get_task(event)
        start_time = event['start']['dateTime'][11:16]
        end_time = event['end']['dateTime'][11:16]
        event_color = get_company_color(company)
        formatted = (
            f"<span style='color: {event_color}; font-weight: bold;'>"
            f"Empresa: {company}<br>"
            f"Tarea: {task}<br>"
            f"Evento: {event['summary']}<br>"
            f"Horario: {start_time} - {end_time}<br>"
            f"Ubicación: {event.get('location', 'N/A')}<br>"
        )
        formatted_events.append(formatted)
    show_info_dialog(
        calendar_window,
        f"Detalles de eventos para {selected_date}",
        "<br>".join(formatted_events)
    )

def load_calendar_data(calendar_window, selected_date):
    """Cargar eventos para una fecha seleccionada desde Google Calendar."""
    try:
        events = get_events()
        events_on_date = [event for event in events if 'start' in event and 'dateTime' in event['start'] and event['start']['dateTime'].startswith(selected_date)]
        return events_on_date
    except Exception as e:
        show_error_dialog(calendar_window, "Error", f"Error al cargar los eventos: {e}")
        return []

# __ Select Date __
def select_date(calendar_window, date):
    """Almacena la fecha seleccionada con un clic simple y actualiza la interfaz."""
    calendar_window.selected_date = date 
    events = load_calendar_data(calendar_window, date.toString("yyyy-MM-dd"))
    calendar_window.btn_edit.setEnabled(bool(events))
    calendar_window.btn_delete.setEnabled(bool(events))

# __ Create, Edit, Save and Delete Events __
def create_event(calendar_window):
    selected_date = calendar_window.calendar.selectedDate().toString("yyyy-MM-dd")
    dialog = QDialog(calendar_window)
    form_layout = QFormLayout(dialog)
    empresas = load_company_options(EXCEL_FILE_PATH, 'datos_empresa')
    if not empresas:
        show_error_dialog(calendar_window, "Error", "No se encontraron empresas en el archivo Excel.")
        return
    calendar_window.company_input = QComboBox(dialog)
    calendar_window.company_input.addItems(empresas)
    calendar_window.task_input = QComboBox(dialog)
    calendar_window.task_input.addItems(TASK_OPTIONS)
    calendar_window.event_name_input = QLineEdit(dialog)
    calendar_window.location_input = QLineEdit(dialog)
    calendar_window.start_hour_input = QTimeEdit(dialog)
    calendar_window.end_hour_input = QTimeEdit(dialog)
    calendar_window.rate_input = QLineEdit(dialog)
    form_layout.addRow("Empresa:", calendar_window.company_input)
    form_layout.addRow("Tarea:", calendar_window.task_input)
    form_layout.addRow("Nombre del evento:", calendar_window.event_name_input)
    form_layout.addRow("Ubicación:", calendar_window.location_input)
    form_layout.addRow("Hora de inicio:", calendar_window.start_hour_input)
    form_layout.addRow("Hora de fin:", calendar_window.end_hour_input)
    btn_save = QPushButton("Guardar")
    btn_save.clicked.connect(lambda: save_event(calendar_window, dialog, selected_date))
    form_layout.addWidget(btn_save)
    dialog.setLayout(form_layout)
    dialog.setWindowTitle("Crear Evento")
    dialog.resize(300, 300)
    dialog.exec()
    refresh_calendar(calendar_window)  # Refrescar el calendario
    show_info_dialog(calendar_window, "Éxito", "Evento creado exitosamente.")  # Mostrar diálogo

def save_event(calendar_window, dialog, selected_date):
    """Guardar el evento personalizado en Google Calendar."""
    company = calendar_window.company_input.currentText()
    company_info = get_company_data(company, load_dataframe(EXCEL_FILE_PATH, sheet_name='datos_empresa'))
    jornada_precio = company_info.get('Jornada_Precio', 0)
    description = f"{jornada_precio}€ {company}"
    task = calendar_window.task_input.currentText()
    event_name = calendar_window.event_name_input.text()
    location = calendar_window.location_input.text()
    start_time = calendar_window.start_hour_input.time().toString("HH:mm")
    end_time = calendar_window.end_hour_input.time().toString("HH:mm")
    start_datetime = f"{selected_date}T{start_time}:00"
    end_datetime = adjust_end_datetime(selected_date, start_time, end_time)
    params = {
        "summary": event_name,
        "location": location,
        "description": description,
        "start": {"dateTime": start_datetime},
        "end": {"dateTime": end_datetime},
        "transparency": "opaque",
        "company": company,
        "task": task,
        "color": get_company_color(company)  # Obtener el color desde la empresa
    }
    try:
        create_event_api(params, calendar_window)
        dialog.accept()
    except Exception as e:
        show_error_dialog(calendar_window, "Error", f"df_coop el evento: {e}")

def edit_event(calendar_window):
    selected_date = calendar_window.calendar.selectedDate().toString("yyyy-MM-dd")
    events = load_calendar_data(calendar_window, selected_date)
    if not events:
        show_info_dialog(calendar_window, "Información", "No hay eventos para editar en esta fecha.")
        return
    event = events[0]
    event_id = event['id']
    dialog = QDialog(calendar_window)
    form_layout = QFormLayout(dialog)
    empresas = load_company_options(EXCEL_FILE_PATH, 'datos_empresa')
    if not empresas:
        show_error_dialog(calendar_window, "Error", "No se encontraron empresas en el archivo Excel.")
        return
    calendar_window.company_input = QComboBox(dialog)
    calendar_window.company_input.addItems(empresas)
    calendar_window.company_input.setCurrentText(get_company_name(event))
    calendar_window.task_input = QComboBox(dialog)
    calendar_window.task_input.addItems(TASK_OPTIONS)
    calendar_window.task_input.setCurrentText(get_task(event))
    calendar_window.event_name_input = QLineEdit(dialog)
    calendar_window.event_name_input.setText(event['summary'])
    calendar_window.location_input = QLineEdit(dialog)
    calendar_window.location_input.setText(event.get('location', ''))
    start_time_str = event['start']['dateTime'][11:16]
    end_time_str = event['end']['dateTime'][11:16]
    start_time = QTime.fromString(start_time_str, "HH:mm")
    end_time = QTime.fromString(end_time_str, "HH:mm")
    calendar_window.start_hour_input = QTimeEdit(dialog)
    calendar_window.start_hour_input.setTime(start_time)
    calendar_window.end_hour_input = QTimeEdit(dialog)
    calendar_window.end_hour_input.setTime(end_time)
    calendar_window.rate_input = QLineEdit(dialog)
    calendar_window.rate_input.setText(event.get('description', ''))
    form_layout.addRow("Empresa:", calendar_window.company_input)
    form_layout.addRow("Tarea:", calendar_window.task_input)
    form_layout.addRow("Nombre del evento:", calendar_window.event_name_input)
    form_layout.addRow("Ubicación:", calendar_window.location_input)
    form_layout.addRow("Hora de inicio:", calendar_window.start_hour_input)
    form_layout.addRow("Hora de fin:", calendar_window.end_hour_input)
    form_layout.addRow("Tarifa:", calendar_window.rate_input)
    btn_save = QPushButton("Guardar")
    btn_save.clicked.connect(lambda: save_edited_event(calendar_window, dialog, event_id, selected_date))
    form_layout.addWidget(btn_save)
    dialog.setLayout(form_layout)
    dialog.setWindowTitle("Editar Evento")
    dialog.resize(300, 300)
    dialog.exec()
    refresh_calendar(calendar_window)  # Refrescar el calendario
    show_info_dialog(calendar_window, "Éxito", "Evento editado guardado exitosamente.")  # Mostrar diálogo

def save_edited_event(calendar_window, dialog, event_id, selected_date):
    """Guardar los cambios del evento editado en Google Calendar."""
    empresas = load_company_options(EXCEL_FILE_PATH, 'datos_empresa')
    if not empresas:
        show_error_dialog(calendar_window, "Error", "No se encontraron empresas en el archivo Excel.")
        return

    company = calendar_window.company_input.currentText()
    company_info = get_company_data(company, load_dataframe(EXCEL_FILE_PATH, 'datos_empresa'))
    
    jornada_precio = company_info.get('Jornada_Precio', 0)
    description = f"{jornada_precio}€ {company}"
    task = calendar_window.task_input.currentText()
    event_name = calendar_window.event_name_input.text()
    location = calendar_window.location_input.text()
    start_time = calendar_window.start_hour_input.time().toString("HH:mm")
    end_time = calendar_window.end_hour_input.time().toString("HH:mm")
    rate = calendar_window.rate_input.text()
    description = get_description(rate, company)
    start_datetime = f"{selected_date}T{start_time}:00"
    end_datetime = adjust_end_datetime(selected_date, start_time, end_time)
    nuevos_datos = {
        "summary": event_name,
        "location": location,
        "description": description,
        "start": {"dateTime": start_datetime},
        "end": {"dateTime": end_datetime},
        "transparency": "opaque",
        "company": company,
        "task": task,
        "color": get_company_color(company)  # Obtener el color desde la empresa
    }
    try:
        edit_event_api(event_id, nuevos_datos, calendar_window)
        dialog.accept()
    except Exception as e:
        show_error_dialog(calendar_window, "Error", f"df_coop los cambios del evento: {e}")

def delete_event(calendar_window):
    """Borrar evento seleccionado en el calendario."""
    selected_date = calendar_window.calendar.selectedDate().toString("yyyy-MM-dd")
    events = load_calendar_data(calendar_window, selected_date)
    if not events:
        show_info_dialog(calendar_window, "Información", "No hay eventos para borrar en esta fecha.")
        return
    event = events[0]
    event_id = event['id']
    if confirm_action(calendar_window, "Confirmar Eliminación", "¿Está seguro de que desea eliminar esta entrada?"):
        try:
            delete_event_api(event_id, calendar_window)
            show_info_dialog(calendar_window, "Éxito", "Evento eliminado exitosamente.")
        except Exception as e:
            show_error_dialog(calendar_window, "Error", f"Error al borrar el evento: {e}")
        format = QTextCharFormat()
        datetime = event['start']['dateTime']
        date = QDate.fromString(datetime[:10], "yyyy-MM-dd")
        calendar_window.calendar.setDateTextFormat(date, format)
        # Filtrar eventos para la fecha seleccionada
        events = [event for event in events if event["start"]["dateTime"].startswith(selected_date)]
    return events

# __ Show Company Stats __

def show_company_stats(calendar_window):
    """Mostrar estadísticas de horas/días por empresa y tarea."""
    print("Mostrando estadísticas de horas/días por empresa y tarea")   
    try:
        events = get_events()
        manager = BusinessManager()
        manager.load_events(events)
        # Mostar ehoras, importe, dias y tareas por empresa
        message = f"Estadísticas del mes {datetime.now().strftime('%Y-%m')}:\n\n"
        message += f"Horas por empresa: {manager.calculate_hours_per_company()}\n"
        print("Acaba de calcular horas por empresa")   
        message += f"Importe por empresa: {manager.calculate_import_per_company()}\n"
        
        # Datos calculados
        print("Calculando horas por empresa...\n")
        hours_per_company = manager.calculate_hours_per_company()
        
        importe_per_company = manager.calculate_import_per_company()
        print("Calculando horas por empresa...\n")
        days_per_company = manager.calculate_days_per_company()
        hours_per_task = manager.calculate_hours_per_task()
        importe_per_task = manager.calculate_import_per_task()
        
        print("Calculando importe por empresa...\n")
        # Construir mensaje
        message = "Estadísticas del Mes Actual:\n\n"
        message += "Horas Trabajadas por Empresa:\n"
        for company, hours in hours_per_company.items():
            message += f"- {company}: {hours:.1f} horas\n"
        
        message += "\n\nDías Trabajados por Empresa y Mes:\n"
        for (company, month), days in days_per_company.items():
            message += f"- {company} en {month}: {days} días\n"
        
        message += "\n\nHoras por Tarea:\n"
        for task, hours in hours_per_task.items():
            message += f"- {task}: {hours:.1f} horas\n"
        
        message += "\n\nImporte Total por Empresa:\n"
        for company, importe in importe_per_company.items():
            message += f"- {company}: {importe:.2f} €\n"
        
        # message += "\n\nImporte por Tarea:\n"
        # for task, importe in importe_per_task.items():
        #     message += f"- {task}: {importe:.2f} €\n"
        
        show_info_dialog(calendar_window,"Estadísticas", message)
    except Exception as e:
        show_error_dialog(calendar_window, "Error", str(e))

def show_company_stats_month(calendar_window, month_str):
    """Mostrar estadísticas de horas/días por empresa y tarea."""
    try:
        events = get_events_by_month(month_str)
        manager = BusinessManager()
        manager.load_events(events)
        # Mostar ehoras, importe, dias y tareas por empresa
        message = f"Estadísticas del mes {month_str}:\n\n"
        message += f"Horas por empresa: {manager.calculate_hours_per_company()}\n"
        message += f"Importe por empresa: {manager.calculate_import_per_company()}\n"
        
        # Datos calculados
        print("Calculando horas por empresa...\n")
        hours_per_company = manager.calculate_hours_per_company()
        
        importe_per_company = manager.calculate_import_per_company()
        print("Calculando horas por empresa...\n")
        days_per_company = manager.calculate_days_per_company()
        hours_per_task = manager.calculate_hours_per_task()
        importe_per_task = manager.calculate_import_per_task()
        
        print("Calculando importe por empresa...\n")
        # Construir mensaje
        message = "Estadísticas del Mes Actual:\n\n"
        message += "Horas Trabajadas por Empresa:\n"
        for company, hours in hours_per_company.items():
            message += f"- {company}: {hours:.1f} horas\n"
        
        message += "\n\nDías Trabajados por Empresa y Mes:\n"
        for (company, month), days in days_per_company.items():
            message += f"- {company} en {month}: {days} días\n"
        
        message += "\n\nHoras por Tarea:\n"
        for task, hours in hours_per_task.items():
            message += f"- {task}: {hours:.1f} horas\n"
        
        message += "\n\nImporte Total por Empresa:\n"
        for company, importe in importe_per_company.items():
            message += f"- {company}: {importe:.2f} €\n"
        
        # message += "\n\nImporte por Tarea:\n"
        # for task, importe in importe_per_task.items():
        #     message += f"- {task}: {importe:.2f} €\n"
        
        show_info_dialog(calendar_window,"Estadísticas", message)
    except Exception as e:
        show_error_dialog(calendar_window, "Error", str(e))

def adjust_end_datetime(selected_date, start_time, end_time):
    """Ajustar la fecha de fin si es posterior a 00:00."""
    start_datetime = f"{selected_date}T{start_time}:00"
    end_datetime = f"{selected_date}T{end_time}:00"
    
    start_datetime_obj = QDateTime.fromString(start_datetime, "yyyy-MM-ddTHH:mm:ss")
    end_datetime_obj = QDateTime.fromString(end_datetime, "yyyy-MM-ddTHH:mm:ss")
    
    if end_datetime_obj < start_datetime_obj:
        end_datetime_obj = end_datetime_obj.addDays(1)
    
    return end_datetime_obj.toString("yyyy-MM-ddTHH:mm:ss")

def get_description(rate, company):
    """Obtener la descripción del evento (tarifa + nombre empresa)."""
    return f"{rate} {company}"
