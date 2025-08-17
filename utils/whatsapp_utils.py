 # feature/ai_color_modify_relevant_message

import os
import datetime
from datetime import datetime as dttime, date as dt, time as dt_time, timedelta
from PyQt6.QtWidgets import QListWidget, QTextEdit
from PyQt6.QtCore import Qt
from utils.calendar_utils import create_event_api, get_company_color, refresh_calendar
from models.chat_parser import (
    load_chats, highlight_keywords, infer_date,
    handle_chat_message, check_availability, nlp, extract_location, extract_time
)
from utils.common_functions import show_info_dialog, show_error_dialog
from utils.event_handler import confirm_event, reject_event
from models.chat_parser import extract_relevant_messages, generate_summary
from utils.gui_utils import create_button
from utils.styles import BUTTON_STYLE, ICON_DIR
from utils.file_utils import select_files, clear_whatsapp_message
from models.chat_parser import load_chats, highlight_keywords, process_chat

def load_and_display_data(main_window):
    try:
        main_window.chats = load_chats()
        main_window.chat_list.clear()
        main_window.chat_list_send.clear()
        for chat in main_window.chats:
            chat_name = chat.get("nombre", "Sin título")
            main_window.chat_list.addItem(chat_name)
            main_window.chat_list_send.addItem(chat_name)
    except Exception as e:
        show_error_dialog(main_window, "Error", f"Error al cargar los chats: {str(e)}")

def process_chat(messages, calendar_window):
    html_output = ''
    previous_date = None
    
    for msg in messages:
        date_str = msg.get("date", "")
        time_str = msg.get("time", "")
        sender = msg.get("sender", "")
        styled_message = msg.get("message", "")
        
        if not date_str:
            continue
        
        try:
            current_date = dttime.strptime(date_str, "%d/%m/%y")
            if date_str != previous_date:
                html_output += f'''
                    <div class="date-header">
                        <strong>{current_date.strftime("%d de %B de %Y")}</strong>
                    </div>
                '''
                previous_date = date_str
        except ValueError:
            continue
        
        # Resaltar keywords
        styled_message = highlight_keywords(styled_message)
        
        # Extraer ubicación y hora
        location = extract_location(styled_message)
        
        # Extraer hora del mensaje del chat
        # time_work_str = extract_time(styled_message)
        
        # Mostrar detalles extraídos
        
        doc = nlp(styled_message)
        for ent in doc.ents:
            if ent.label_ == 'DATE':
                styled_message = styled_message.replace(
                    ent.text,
                    f'<span class="highlight">{ent.text}</span>'
                )
        
        # Generar botones de disponibilidad
        if "disponible" in styled_message.lower() or "libre" in styled_message.lower():
            date, time_ = infer_date(styled_message)  
            if date and isinstance(date, dt): 
                response = handle_chat_message(styled_message, calendar_window)
                if time_ and isinstance(time_,dt_time) and time_ != dt_time(0, 0):
                    formatted_time = time_.strftime("%H.%M")
                else:
                    formatted_time = "09.00"  # Hora por 
                formatted_date = date.strftime("%d-%m-%Y")
                datetime_str = f"{formatted_date}T{formatted_time}"
                styled_message += f"""
                    <div class="disponibilidad normal">
                        {response}
                        <a href='confirm://{datetime_str}'>Confirmar</a> |
                        <a href='reject://{datetime_str}'>Rechazar</a>
                    </div>
                """
        
        # Bloque de mensaje con estilo original
        html_output += f'''
            <div class="message-block">
                <div class="timestamp" title="{date_str}">
                    {time_str} - {sender}:
                </div>
                <div class="message-content">
                    {styled_message}
                </div>
                <hr class="message-divider">
            </div>
        '''
    
    return f'''
        <html>
        <head>
            <style>
                /* Estilos originales */
                body {{
                    background-color: #333;
                    color: white;
                    font-family: Arial, sans-serif;
                    padding: 10px;
                }}
                .date-header {{
                    text-align: center;
                    margin: 20px 0;
                    padding: 8px 12px;
                    background-color: #424242;
                    border-radius: 5px;
                    font-size: 1.1em;
                    color: #EEEEEE;
                }}
                .message-block {{
                    margin: 15px 0;
                    padding: 10px;
                    background-color: #212121;
                    border-radius: 5px;
                    position: relative;
                }}
                .timestamp {{
                    background-color: #000000;
                    color: white;
                    font-size: 0.9em;
                    padding: 5px 10px;
                    border-radius: 3px;
                    display: inline-block;
                    margin-bottom: 8px;
                }}
                .message-content {{
                    margin: 10px 0;
                    padding: 5px;
                    line-height: 1.4em;
                }}
                .highlight {{
                    background-color: #00d4ff;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-weight: bold;
                }}
                .disponibilidad {{
                    display: block;
                    margin: 10px 0;
                    padding: 8px;
                    border-radius: 5px;
                    font-weight: bold;
                    color: white;
                }}
                .disponibilidad.normal {{
                    background-color: #4CAF50;
                }}
                .disponibilidad.error {{
                    background-color: #FF5722;
                }}
                .message-divider {{
                    border: none;
                    border-top: 1px solid #424242;
                    margin: 12px 0;
                }}
                /* Estilos para información extraída */
                .location-info {{
                    margin: 5px 0;
                    padding: 2px 4px;
                    border-radius: 3px;
                    background-color: #001a00; /* Fondo muy oscuro para verde */
                }}
                .time-info {{
                    margin: 5px 0;
                    padding: 2px 4px;
                    border-radius: 3px;
                    background-color: #000d1a; /* Fondo muy oscuro para azul */
                }}
            </style>
        </head>
        <body>
            <div class="chat-container">
                {html_output}
            </div>
        </body>
        </html>
    '''

def update_chat_content(main_window, current_item, list_widget):
    if current_item:
        selected_chat_name = current_item.text()
        for chat in main_window.chats:
            if chat["nombre"] == selected_chat_name:
                # Usar mensajes con campos válidos
                valid_messages = [
                    msg for msg in chat.get("messages", [])
                    if isinstance(msg, dict) and "date" in msg and "message" in msg
                ]
                formatted_chat = process_chat(valid_messages, main_window.calendar_window)
                main_window.chat_content.setHtml(formatted_chat)
                break

def create_event_from_message(message, calendar_window):
    inferred = infer_date(message)
    if not inferred:
        return False, "No se pudo inferir la fecha."

    start = inferred
    end = start + timedelta(days=1)

    task = "Tarea no especificada"
    location = "Ubicación no especificada"
    for keyword in ["instalar", "operar", "mantenimiento"]:
        if keyword in message.lower():
            task = keyword.title()

    if check_availability(start, end, calendar_window):
        create_event_api({
            "summary": f"{task} - {start.strftime('%d/%m/%Y')}",
            "location": location,
            "description": message,
            "start": {
                "dateTime": f"{start.isoformat()}T09:00:00Z",
                "timeZone": "Europe/Madrid"
            },
            "end": {
                "dateTime": f"{end.isoformat()}T17:00:00Z",
                "timeZone": "Europe/Madrid"
            },
            "extendedProperties": {
                "private": {
                    "company": "Empresa por defecto",
                    "task": task,
                    "color": get_company_color("Empresa por defecto")
                }
            }
        })
        refresh_calendar(calendar_window)
        return True, "Evento creado exitosamente"
    else:
        return False, "No hay disponibilidad en ese horario"
      
                # Pasar solo los mensajes, no todo el chat
                formatted_chat = process_chat(chat["messages"])  
                main_window.chat_content.setHtml(formatted_chat)  
                break

def send_wpp(main_window):
    # 1. Obtener el texto del mensaje
    message = main_window.message_input.toPlainText()
    selected_chat = main_window.chat_list_send.currentItem()
    destinatario = selected_chat.text() if selected_chat else "Sin destinatario"
    
    # Acceder directamente al QListWidget de adjuntos
    attached_files_list_widget = main_window.attach_list 
    attached_files = []
    for i in range(attached_files_list_widget.count()):
        item = attached_files_list_widget.item(i)
        attached_files.append(item.text())
    
    
    message_text = f"El mensaje:\n\n{message}"
    
    
    if attached_files:
        files_str = "\n- " + "\n- ".join(attached_files)
        message_text += f"\n\nArchivos adjuntos:{files_str}"
    
    message_text += f"\n\nSerá enviado a '{destinatario}' por WhatsApp.\nAPIs de Meta no están disponibles."
    
    show_info_dialog(main_window, "Mensaje preparado", message_text)

def confirm_wpp(main_window):
    main_window.message_input.setText(
        "Confirmo la disponibilidad para las fechas indicadas. Evento creado en el calendario."
    )

def reject_wpp(main_window):
    main_window.message_input.setText(
        "Lamentablemente no hay disponibilidad para esas fechas. ¿Desea programar para otra fecha?"
    )

def clear_whatsapp_message(chat_list, compose_area, attach_list)
    compose_area.clear()
    attach_list.clear()
