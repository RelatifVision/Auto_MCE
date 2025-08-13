# utils/event_handler.py
from datetime import datetime, timedelta, timezone
from PyQt6.QtCore import Qt
from calendar_api_setting.calendar_api import create_event_api, refresh_calendar
from utils.common_functions import show_info_dialog, show_error_dialog
from utils.company_utils import get_company_color


def confirm_event(calendar_window, date, time_str=None, location=None):
    # Definir horario por defecto si no hay
    start_time = datetime.strptime(time_str or "09:00", "%H:%M").time()
    end_time = (datetime.combine(date, start_time) + timedelta(hours=10)).time()
    
    # Crear evento con detalles extraídos
    create_event_api({
        "summary": f"Confirmado - {date.strftime('%d/%m/%Y')}",
        "location": location or "Ubicación no especificada",
        "description": f"Ubicación: {location}\nHorario: {time_str}",
        "start": {"dateTime": datetime.combine(date, start_time).isoformat() + "Z"},
        "end": {"dateTime": datetime.combine(date, end_time).isoformat() + "Z"},
        "extendedProperties": {"private": {"company": "Empresa por defecto"}}
    })
    refresh_calendar(calendar_window)
    show_info_dialog(calendar_window, "Éxito", "Evento creado exitosamente")
    
def create_event_from_form(dialog, date, company="Empresa por defecto", task="Tarea no especificada", location="Ubicación no especificada", summary=None):
    """Crear evento desde formulario con datos por defecto"""
    try:
        start_dt = datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc)
        end_dt = start_dt + timedelta(days=1)
        
        if not summary:
            summary = f"Confirmado - {date.strftime('%d/%m/%Y')}"
        
        create_event_api({
            "summary": summary,
            "location": location,
            "description": f"Empresa: {company}, Tarea: {task}",
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "Europe/Madrid"
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "Europe/Madrid"
            },
            "extendedProperties": {
                "private": {
                    "company": company,
                    "task": task,
                    "color": get_company_color(company) or "#4CAF50"
                }
            }
        }, dialog.parent())
        
        refresh_calendar(dialog.parent().calendar_window)
        show_info_dialog("Éxito", "Evento creado exitosamente")
        dialog.accept()
    except Exception as e:
        show_error_dialog(dialog.parent(), "Error", f"Error al crear evento: {str(e)}")

def reject_event(window):
    show_info_dialog(window, "Rechazado", "Solicitud rechazada")