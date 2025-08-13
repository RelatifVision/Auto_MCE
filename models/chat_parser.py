import os
import re
import pandas as pd
import spacy
import random
import datetime
from datetime import datetime as dttime, date, time as dtime, timedelta, timezone # Renombramos para evitar conflictos

import dateparser
from calendar_api_setting.calendar_api import get_events
from utils.common_functions import show_error_dialog
from utils.event_handler import confirm_event, reject_event

# Load the spaCy model
nlp = spacy.load("es_core_news_lg")

def is_relevant_message(message):
    """
    Determina si un mensaje es relevante basado en su contenido.
    :param message: El contenido del mensaje.
    :return: True si el mensaje es relevante, False en caso contrario.
    """
    # Expresiones regulares para detectar información relevante
    patterns = [
        r'\b(horario|hora|mañana|tarde|noche|cita|disponibilidad|nocturnidad|pasado|mes siguiente|próximo)\b',  # Horarios
        r'\b(ubicación|dirección|lugar|envío|localización|sede|oficina|local|calle|avenida|paseo|nave|hotel|plaza)\b'  # Ubicaciones,
        r'\b(precio|tarifa|coste|valor|factura|pedido|importe|presupuesto|cotización)\b',  # Presupuestos
        r'\b(urgente|importante|revisar|última|último|urgencia|inmediato|necesito|requiero)\b',  # Urgencias
        r'\b(\d{1,2} de (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre))\b',  # Fechas específicas
        r'\b(operar|realizar|instalar|desmontar|programar|hacer|programación|configuración|instalación|montaje|mantenimiento|streaming|pantalla|tiras led|led|iluminación|luz|MA2|MA3|chamsys|resolume|novastar|procesador|escalador|sender|tarima|m|técnico de contenido|vimix|obs|h2|h5|h7)\b',  # Tareas/Equipos
    ]
    for pattern in patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    return False

def extract_relevant_messages(chat, color):
    messages = []
    for msg in chat["messages"]:
        messages.append({
            "datetime": msg["fecha"],
            "sender": msg["sender"],
            "text": msg["mensaje"],
            "color": color
        })
    return messages

def extract_location(text):
    """Extrae ubicación después de 'es en', 'estar en', o palabras clave como 'ubicación'"""
    matches = [
        re.search(r'\b(es|estar)\s+en\s+([^.\n]+)', text, re.IGNORECASE),
        re.search(r'\b(ubicación|dirección|lugar)\s*:?\s*([^.\n]+)', text, re.IGNORECASE)
    ]
    
    for match in matches:
        if match:
            return match.group(2).strip()
    
    return None

def extract_time(text):
    """Extrae hora después de 'a las', 'sobre la' o palabras clave como 'hora'"""
    matches = [
        re.search(r'\b(a las|sobre la|sobre las)\s+([0-2]\d:[0-5]\d)\b', text, re.IGNORECASE),
        re.search(r'\b(hora)\s*:?\s*([0-2]\d:[0-5]\d)\b', text, re.IGNORECASE)
    ]
  
    for match in matches:
        if match:
            return match.group(2)
    
    return None

# Función para resaltar palabras clave (adaptada de tu código)
def highlight_keywords(text):
    patterns = [
        # Presupuestos con IVA
        (r'\b\d{1,3}[,.]?\d{1,2}\s*[€$£¥₩]?\s*\+\s*IVA\b', '#ffbf00', 'bold'),
        (r'\b\d{1,3}[,.]?\d{1,2}\s*[€$£¥₩]\b', '#ffbf00', 'bold'),
        
        # Fechas (formatos variados)
        (r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '#0077ff', 'bold'),
        (r'\b\d{1,2}\s+de\s+\w+\b', '#0077ff', 'bold'),
        
        # Horarios 
        (r'\b(?:[01]?\d|2[0-3])(?::|\.)[0-5]\d\b', '#00d4ff', 'bold'),
        # Frases de horario
        (r'\b(a las|sobre la|sobre las)\s+([0-2]\d:[0-5]\d)\b', '#00d4ff', 'bold'),
        (r'\b(hora|tiempo)\s*:?\s*([0-2]\d:[0-5]\d)\b', '#00d4ff', 'bold'), 
        
        
        # Frases de ubicación
        (r'\b(es|estar)\s+en\s+([^.\n]+)', '#00ff32', 'bold'),
        (r'\b(ubicación|dirección|lugar)\s*:?\s*([^.\n]+)', '#00ff32', 'bold'),
        

        # Días de la semana y relativos
        (r'\b(hoy|mañana|pasado|próximo|lunes|martes|miercoles|jueves|viernes|sabado|domingo)\b', '#0077ff', 'bold'),
        
        # Urgencias
        (r'\b(urgente|inmediato|necesito|prioridad|ya|ahora|requiero)\b', '#ff5c00', 'bold'),
        
        # Eventos
        (r'\b(evento|reunión|presentación|taller|concierto|obra|feria|muestra)\b', "#00ff88", 'bold'),
        
        # Tareas/Equipos
        (r'\b(operar|instalar|mantenimiento|streaming|pantalla|tiras led|led|iluminación)\b', '#9200ff', 'bold'),
    ]

    for pattern, color, weight in patterns:
        text = re.sub(
            pattern,
            f'<span style="color: {color}; font-weight: {weight}">\\g<0></span>',
            text,
            flags=re.IGNORECASE | re.UNICODE
        )
    
    return text

# Función para procesar el chat
def load_chats(directory="data/chats"):
    chats = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            chat_name = os.path.splitext(filename)[0]
            chat_data = {"nombre": chat_name, "messages": []}
            
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as file:
                for line in file:
                    match = re.match(r'(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}) - ([^:]+): (.+)', line.strip())
                    if match:
                        date_str, time_str, sender, message = match.groups()
                        chat_data["messages"].append({
                            "date": date_str,
                            "time": time_str,
                            "sender": sender,
                            "message": message
                        })
            chats.append(chat_data)
    return chats

def infer_date(text):
    today = dttime.now().date()
    parsed = dateparser.parse(text, languages=['es'], settings={'DATE_ORDER': 'DMY'})
    if parsed:
        return parsed.date(), parsed.time()  # Devolver fecha
    
    # 2. Lógica para fechas como "12 de agosto"
    match = re.search(r'\b(\d{1,2})\s+de\s+(\w+)\b', text, re.IGNORECASE)
    if match:
        day = match.group(1)
        month = match.group(2).capitalize()
        parsed = dateparser.parse(f"{day} {month}", settings={'DATE_ORDER': 'DMY'})
        if parsed:
            return dttime.combine(parsed.date(), parsed.time(), tzinfo=timezone.utc), datetime.time(9, 0)
    
    # 3. Lógica para palabras clave
    lowered = text.lower()
    if "mañana" in lowered:
        return datetime.combine(
            today + timedelta(days=1),
            dttime.min.time(),
            tzinfo=timezone.utc
        ), datetime.time(9, 0)
    elif "próximo" in lowered:
        return datetime.combine(
            today + timedelta(weeks=1),
            dttime.min.time(),
            tzinfo=timezone.utc
        ), datetime.time(9, 0)
    elif "dentro de" in lowered:
        match = re.search(r'dentro de (\d+)', lowered)
        if match:
            days = int(match.group(1))
            return datetime.combine(
                today + timedelta(days=days),
                dttime.min.time(),
                tzinfo=timezone.utc
            ), datetime.time(9, 0)
    
    parsed = dateparser.parse(text, languages=['es'], settings={'DATE_ORDER': 'DMY'})
    if parsed:
        return parsed.date()
    
    # Fallback: hoy a las 09:00
    return today, datetime.time(9, 0) 

def handle_chat_message(message, calendar_window):
    inferred_date, time_str_unused = infer_date(message)
    if not inferred_date:
        return "No se entendió la fecha."
    
    # Extraer horario y ubicación
    time_str = extract_time(message)
    location = extract_location(message)
    
    # Usar horario extraído o por defecto
    start_time = datetime.datetime.strptime(time_str, "%H:%M").time() if time_str else datetime.time(9, 0)
    end_time = (datetime.datetime.combine(datetime.date.today(), start_time) + datetime.timedelta(hours=10)).time()  # 10 horas
    
    # Crear datetime completo
    start_dt = dttime.combine(inferred_date, start_time)
    end_dt = dttime.combine(inferred_date, end_time)
    
    if check_availability(start_dt, end_dt, calendar_window):
        return f"Disponible para {location or 'ubicación no especificada'} a las {time_str or '09:00-19:00'}. ¿Crear evento?"
    else:
        return "No hay disponibilidad en ese horario."

def check_availability(start_dt, end_dt, calendar_window):
    events = get_events()
    start_date = start_dt.date()
    end_date = end_dt.date()
    
    for event in events:
        try:
            event_start = dateparser.parse(event['start']['dateTime']).date()
            event_end = dateparser.parse(event['end']['dateTime']).date()
            
            if start_date < event_end and end_date > event_start:
                return False  # Hay conflicto
        except KeyError:
            continue
    return True

def generate_summary(messages):
    """
    Generar un resumen de las tareas y horarios basados en los mensajes relevantes.
    """
    summary_dict = {}
    for message in messages:
        date = message['date']
        if date not in summary_dict:
            summary_dict[date] = []
        summary_dict[date].append(message)

    summary = ""
    last_date = None
    last_chat = None
    for date in sorted(summary_dict.keys()):
        if last_date and last_date != date:
            summary += "<br><br>"  # Doble salto de línea al cambiar de fecha
        summary += f"El día {date}: "
        for message in summary_dict[date]:
            if last_chat and last_chat != message['color']:
                summary += "<br>"  # salto de línea al cambiar de chat
            # Generar texto natural con spaCy
            doc = nlp(message['text'])
            summary_text = " ".join([sent.text for sent in doc.sents])
            summary += f"<br> - {message['time']} - {message['sender']}: {summary_text} "
            last_chat = message['color']
        last_date = date
        summary += "<>"  # Salto de línea por cada mensaje diferente

    # Generar un resumen general con spaCy
    sender_texts = {}
    resumen_general = ""
    for msg in messages:
        sender = msg['sender']
        if sender not in sender_texts:
            sender_texts[sender] = []
        sender_texts[sender].append(msg['text'])
        
    for sender, value in sender_texts.items():
        
        value = "<br> ".join(string for string in value)
        doc = nlp(value)
        resumen_general += f"{sender}: ".join([f"{sent.text}<br><br>" for sent in doc.sents])
    summary += f"<br><br>Resumen General:<br><br>{resumen_general}"

    return summary