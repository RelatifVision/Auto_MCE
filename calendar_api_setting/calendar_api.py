#å calendar_api_settings\calendar_api.py
import os
import calendar
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from config import SERVICE_ACCOUNT_FILE, CALENDAR_ID, TASK_OPTIONS, EXCEL_FILE_PATH
from PyQt6.QtGui import QColor, QTextCharFormat
from PyQt6.QtCore import QDate
from utils.common_functions import show_error_dialog
from utils.excel_utils import load_dataframe
from utils.company_utils import get_company_color, get_company_name, get_company_data

# Verificar si el archivo existe antes de continuar
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    raise Exception(f"El archivo de service account file no se encuentra en la ruta especificada: {SERVICE_ACCOUNT_FILE}")

# Alcances requeridos para la API de Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Obtener credenciales desde la cuenta de servicio
def get_credentials():
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return creds
    except Exception as e:
        print(f"Error al cargar las credenciales: {e}")
        raise

# Crear un evento en el calendario usando la cuenta de servicio
def create_event_api(params, calendar_window=None):
    credentials = get_credentials()
    # Construir el servicio de Google Calendar
    service = build('calendar', 'v3', credentials=credentials)

    evento = {
        "summary": params["summary"],
        "location": params["location"],
        "description": params["description"],
        "start": {
            "dateTime": params["start"]["dateTime"],
            "timeZone": params.get("timezone", "Europe/Madrid"),
        },
        "end": {
            "dateTime": params["end"]["dateTime"],
            "timeZone": params.get("timezone", "Europe/Madrid"),
        },
        "transparency": params["transparency"],
        "extendedProperties": {
            "private": {
                "company": params["company"],
                "task": params.get("task", "Sin tarea"),  # Asegúrate de incluir "task"
                "color": params["color"]
            }
        }
    }

    try:
        # Llamar a la API para crear el evento en el calendario
        event = service.events().insert(calendarId=CALENDAR_ID, body=evento).execute()
        print(f"Evento creado: {event['summary']}")
    except Exception as e:
        print(f"Error al crear el evento: {e}")
        if calendar_window:
            show_error_dialog(calendar_window, "Error", f"Error al crear el evento: {str(e)}")
        raise
    finally:
        if calendar_window:
            refresh_calendar(calendar_window)

def get_events():
    credentials = get_credentials()
    # Construir el servicio de Google Calendar
    service = build('calendar', 'v3', credentials=credentials)
    try:
        eventos = service.events().list(
            calendarId=CALENDAR_ID,
            singleEvents=True,
            orderBy='startTime',
            timeMin='2024-12-31T00:00:00Z',  # Filtrar eventos desde el 31 de diciembre de 2024
            timeMax='2030-12-31T23:59:59Z',  # Filtrar eventos hasta el 31 de diciembre de 2030
            fields='nextPageToken,items(id,summary,start,end,location,description,extendedProperties)'
        ).execute()
        eventos_lista = eventos.get('items', [])
        return eventos_lista
    except Exception as e:
        print(f"Error al obtener los eventos: {e}")
        return []

def get_events_by_month(month_str):
    """Obtener eventos de un mes específico en formato 'YYYY-MM'."""
    credentials = get_credentials()
    service = build('calendar', 'v3', credentials=credentials)

    # Parsear el mes ingresado (ej: '2025-04')
    year, month = map(int, month_str.split('-'))

    # Calcular primer y último día del mes
    first_day = f"{year}-{month:02d}-01T00:00:00Z"
    last_day = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}T23:59:59Z"

    try:

        eventos = service.events().list(
            calendarId=CALENDAR_ID,
            singleEvents=True,
            orderBy='startTime',
            timeMin=first_day,  # Filtrar eventos desde el 31 de diciembre de 2024
            timeMax=last_day,  # Filtrar eventos hasta el 31 de diciembre de 2030
            fields='nextPageToken,items(id,summary,start,end,location,description,extendedProperties)'
        ).execute()
        eventos_lista = eventos.get('items', [])
        return eventos_lista
    except Exception as e:
        print(f"Error al obtener los eventos: {e}")
        return []

# Borrar un evento desde el calendario usando la cuenta de servicio
def delete_event_api(event_id, calendar_window=None):
    """Borrar evento y refrescar calendario."""
    credentials = get_credentials()
    # Construir el servicio de Google Calendar
    service = build('calendar', 'v3', credentials=credentials)
    try:
        # Eliminar el evento utilizando su ID y el ID del calendario proporcionado
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        print(f"El evento con ID {event_id} ha sido eliminado correctamente del calendario {CALENDAR_ID}.")
    except Exception as e:
        print(f"Error al eliminar el evento: {e}")
        if calendar_window:
            show_error_dialog(calendar_window, "Error", f"Error al eliminar el evento: {str(e)}")
    finally:
        if calendar_window:
            refresh_calendar(calendar_window)

# Modificar un evento en el calendario usando la cuenta de servicio
def edit_event_api(event_id, nuevos_datos, calendar_window=None):
    """Editar evento y refrescar calendario."""
    creds = get_credentials()
    # Construir el servicio de Google Calendar
    service = build('calendar', 'v3', credentials=creds)
    try:
        # Obtener el evento original
        evento = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
        # Actualizar los campos del evento con los nuevos datos
        evento['summary'] = nuevos_datos.get('summary', evento['summary'])
        evento['location'] = nuevos_datos.get('location', evento.get('location'))
        evento['description'] = nuevos_datos.get('description', evento.get('description'))
        evento['start'] = {'dateTime': nuevos_datos.get('start')['dateTime'], 'timeZone': 'Europe/Madrid'}
        evento['end'] = {'dateTime': nuevos_datos.get('end')['dateTime'], 'timeZone': 'Europe/Madrid'}
        evento['transparency'] = nuevos_datos.get('transparency', 'opaque')  # 'opaque' o 'transparent'
        evento['extendedProperties'] = {
            "private": {
                "company": nuevos_datos["company"],
                "task": nuevos_datos.get("task", "Sin tarea"),  # Asegúrate de incluir "task"
                "color": nuevos_datos["color"]
            }
        }
        # Actualizar el evento
        evento_actualizado = service.events().update(
            calendarId=CALENDAR_ID,
            eventId=event_id,
            body=evento
        ).execute()
        print(f"El evento con ID {event_id} ha sido actualizado correctamente.")
        print(f"Nuevo actualización: {evento_actualizado['summary']}")
    except HttpError as error:
        print(f"Error al modificar el evento: {error}")
        if calendar_window:
            show_error_dialog(calendar_window, "Error", f"Error al modificar el evento: {str(error)}")
    finally:
        if calendar_window:
            refresh_calendar(calendar_window)

def refresh_calendar(calendar_window):
    """Refrescar el calendario."""
    try:
        events = get_events()
        for event in events:
            company = get_company_name(event)
            df_comp = load_dataframe(EXCEL_FILE_PATH, 'datos_empresa')
            company_info = get_company_data(company, df_comp)
            start_date_str = event['start']['dateTime'][:10]
            start_date = QDate.fromString(start_date_str, "yyyy-MM-dd")
            color = company_info.get('Color', '#000000')

            format = QTextCharFormat()
            format.setBackground(QColor(color))
            calendar_window.calendar.setDateTextFormat(start_date, format)
    except Exception as e:
        show_error_dialog(calendar_window, "Error", f"Error al refrescar: {str(e)}")