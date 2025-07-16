import os
from datetime import datetime, date, timedelta
from PyQt6.QtWidgets import QListWidget, QTextEdit
from PyQt6.QtCore import Qt
from utils.calendar_utils import create_event_api, get_company_color, refresh_calendar
from models.chat_parser import (
    load_chats, highlight_keywords, infer_date,
    handle_chat_message, check_availability, nlp
)
from utils.common_functions import show_info_dialog, show_error_dialog
<<<<<<< Updated upstream
from models.chat_parser import extract_relevant_messages, generate_summary
from utils.gui_utils import create_button
from utils.styles import BUTTON_STYLE, ICON_DIR
from utils.file_utils import select_files, clear_whatsapp_message
from models.chat_parser import load_chats

def load_chats():
    """
    Cargar lista de chats desde archivos .txt en la carpeta 'data/chats'.
    """
    chats_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/chats"))
    chat_files = [f for f in os.listdir(chats_dir) if f.endswith(".txt")]
    
    chats = []
    for filename in chat_files:
        chat_path = os.path.join(chats_dir, filename)
        with open(chat_path, "r", encoding="utf-8") as file:
            content = file.read()
            chat_name = os.path.splitext(filename)[0]
            chats.append({
                "filename": filename,
                "nombre": chat_name,
                "contenido": content
            })
    return chats
=======
from utils.event_handler import confirm_event, reject_event
>>>>>>> Stashed changes

def load_and_display_data(main_window):
    """
    Cargar y mostrar los datos de los chats.
    """
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
            current_date = datetime.strptime(date_str, "%d/%m/%y")
            if date_str != previous_date:
                html_output += f'''
                    <div class="date-header">
                        <strong>{current_date.strftime("%d de %B de %Y")}</strong>
                    </div>
                '''
                previous_date = date_str
        except ValueError:
            continue

        # Destacar entidades temporales con spaCy
        doc = nlp(styled_message)
        for ent in doc.ents:
            if ent.label_ == 'DATE':
                styled_message = styled_message.replace(
                    ent.text,
                    f'<span class="highlight">{ent.text}</span>'
                )

        inferred = infer_date(styled_message)

        if "disponible" in styled_message.lower():
            if inferred and isinstance(inferred, date):
                response = handle_chat_message(styled_message, calendar_window)
                styled_message += f"""
                    <div class="disponibilidad normal">
                        {response}
                        <a href='confirm://{inferred.strftime("%Y-%m-%d-%H-%M")}'>Confirmar</a> |
                        <a href='reject://{inferred.strftime("%Y-%m-%d-%H-%M")}'>Rechazar</a>
                    </div>
                """
            else:
                styled_message += "<div class='error'>No se entendió la fecha.</div>"

        elif "no hay disponibilidad" in styled_message.lower():
            styled_message += f"""
                <div class="disponibilidad error">
                    {styled_message}
                </div>
            """

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
    # print (f'''
    #     <html>
    #     <head>
    #         <style>
    #             body {{
    #                 background-color: #333;
    #                 color: white;
    #                 font-family: Arial, sans-serif;
    #                 padding: 10px;
    #             }}
    #             .date-header {{
    #                 text-align: center;
    #                 margin: 20px 0;
    #                 padding: 8px 12px;
    #                 background-color: #424242;
    #                 border-radius: 5px;
    #                 font-size: 1.1em;
    #                 color: #EEEEEE;
    #             }}
    #             .message-block {{
    #                 margin: 15px 0;
    #                 padding: 10px;
    #                 background-color: #212121;
    #                 border-radius: 5px;
    #                 position: relative;
    #             }}
    #             .timestamp {{
    #                 background-color: #000000;
    #                 color: white;
    #                 font-size: 0.9em;
    #                 padding: 5px 10px;
    #                 border-radius: 3px;
    #                 display: inline-block;
    #                 margin-bottom: 8px;
    #             }}
    #             .message-content {{
    #                 margin: 10px 0;
    #                 padding: 5px;
    #                 line-height: 1.4em;
    #             }}
    #             .highlight {{
    #                 background-color: #00d4ff;
    #                 padding: 2px 4px;
    #                 border-radius: 3px;
    #                 font-weight: bold;
    #             }}
    #             .disponibilidad {{
    #                 display: block;
    #                 margin: 10px 0;
    #                 padding: 8px;
    #                 border-radius: 5px;
    #                 font-weight: bold;
    #                 color: white;
    #             }}
    #             .disponibilidad.normal {{
    #                 background-color: #4CAF50;
    #             }}
    #             .disponibilidad.error {{
    #                 background-color: #FF5722;
    #             }}
    #             .disponibilidad a {{
    #                 color: white;
    #                 text-decoration: none;
    #                 margin: 0 5px;
    #                 padding: 3px 7px;
    #                 border-radius: 3px;
    #             }}
    #             .disponibilidad a:hover {{
    #                 background-color: #616161;
    #             }}
    #             .message-divider {{
    #                 border: none;
    #                 border-top: 1px solid #424242;
    #                 margin: 12px 0;
    #             }}
    #         </style>
    #     </head>
    #     <body>
    #         <div class="chat-container">
    #             {html_output}
    #         </div>
    #     </body>
    #     </html>''')
    
    return f'''
        <html>
        <head>
            <style>
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
                .disponibilidad a {{
                    color: white;
                    text-decoration: none;
                    margin: 0 5px;
                    padding: 3px 7px;
                    border-radius: 3px;
                }}
                .disponibilidad a:hover {{
                    background-color: #616161;
                }}
                .message-divider {{
                    border: none;
                    border-top: 1px solid #424242;
                    margin: 12px 0;
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
<<<<<<< Updated upstream
        
        # Actualizar contenido del chat solo si es el listado superior
        if list_widget == main_window.chat_list:
            for chat in main_window.chats:
                if chat["nombre"] == selected_chat_name:
                    main_window.chat_content.setPlainText(chat["contenido"])
                    break
                
        # Actualizar destinatario solo si es el listado inferior
        if list_widget == main_window.chat_list_send:
            main_window.destination_input.setText(selected_chat_name)
=======
        for chat in main_window.chats:
            if chat["nombre"] == selected_chat_name:
                valid_messages = [
                    msg for msg in chat.get("messages", [])
                    if isinstance(msg, dict) and "date" in msg
                ]
                formatted_chat = process_chat(valid_messages, main_window.calendar_window)
                main_window.chat_content.setHtml(formatted_chat)
                break
>>>>>>> Stashed changes

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

def send_wpp(main_window):
    message = main_window.message_input.toPlainText()
    selected_chat = main_window.chat_list_send.currentItem()
    destinatario = selected_chat.text() if selected_chat else "Sin destinatario"
    show_info_dialog("Mensaje preparado", f"Mensaje listo para enviar a '{destinatario}':\n\n{message}")

def confirm_wpp(main_window):
    main_window.message_input.setText(
        "Confirmo la disponibilidad para las fechas indicadas. Evento creado en el calendario."
    )

def reject_wpp(main_window):
    main_window.message_input.setText(
        "Lamentablemente no hay disponibilidad para esas fechas. ¿Desea programar para otra fecha?"
    )


def clear_whatsapp_message(chat_list, compose_area, attach_list):
    chat_list.setCurrentRow(-1)
    compose_area.clear()
    attach_list.clear()
