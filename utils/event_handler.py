# utils/event_handler.py
from datetime import datetime, timedelta, timezone
from PyQt6.QtCore import Qt
from calendar_api_setting.calendar_api import create_event_api, refresh_calendar
from utils.common_functions import show_info_dialog, show_error_dialog
from utils.company_utils import get_company_color


def confirm_event(calendar_window, date):
    start_dt = datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc)
    end_dt = start_dt + timedelta(days=1) # Evento de un día completo
    create_event_api({
        "summary": f"Confirmado - {date.strftime('%d/%m/%Y')}",
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
                "company": "Empresa por defecto",
                "task": "Confirmación de disponibilidad"
            }
        }
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

def reject_event():
    show_info_dialog("Rechazado", "Solicitud rechazada")