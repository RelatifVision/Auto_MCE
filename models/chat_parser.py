# models/chat_parser.py
import os
import re
import pandas as pd
import spacy
import random
from datetime import datetime, timedelta
import dateparser

# Load the spaCy model
nlp = spacy.load("es_core_news_lg")

def is_relevant_message(message):
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

# Función para resaltar palabras clave (adaptada de tu código)
def highlight_keywords(text):
    patterns = [
        
        # Presupuestos (con decimales y texto adicional)
        (r'\b\d{1,3}[,.]?\d{1,2}\s*[€$£¥₩]|(?:[€$£¥₩]\d{1,3}[,.]?\d{1,2})\b', '#ffbf00', 'bold'),
        
        # Fechas (formatos variados)
        (r'\b(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{1,2}\s+de\s+\w+|\w+\s+\d{1,2})\b', '#0077ff', 'bold'),
        
        # Horarios
        (r'\b(?:[01]\d|2[0-3]):[0-5]\d\b', '#00d4ff', 'bold'),
        
        # Días de la semana y relativos
        (r'\b(hoy|mañana|pasado|próximo|lunes|martes|miércoles|jueves|viernes|sábado|domingo)\b', '#00d4ff', 'bold'),
        
        # Urgencias
        (r'\b(urgente|inmediato|necesito|prioridad|ya|ahora)\b', '#ff5c00', 'bold'),
        
        # Nombres de eventos
        (r'\b(evento|reunión|presentación|taller|concierto|obra|feria|muestra)\b', "#00ff88", 'bold'), 
        
        # Tareas/Equipos (naranja)
        (r'\b(operar|realizar|instalar|desmontar|programar|hacer|programación|configuración|instalación|montaje|mantenimiento|streaming|pantalla|tiras led|led|iluminación|luz|MA2|MA3|chamsys|resolume|novastar|procesador|escalador|sender|tarima|m|técnico de contenido|vimix|obs|h2|h5|h7)\b', '#9200ff', 'bold'),
        
        # Ubicaciones (verde claro)
        (r'\b(ubicación|dirección|lugar|envío|localización|sede|oficina|local|calle|avenida|paseo|nave|hotel|plaza)\b', '#00ff32', 'bold'),
        
        # Nombres de eventos
        (r'\b(evento|reunión|presentación|taller|concierto|obra|feria|muestra)\b', "#00ff88", 'bold'),

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
def process_chat(messages):
    html_output = ''
    previous_date = None
    for msg in messages:
        date_str = msg["date"]
        time_str = msg["time"]
        sender = msg["sender"]
        styled_message = msg["message"]
        formatted_date = datetime.strptime(date_str, "%d/%m/%y").strftime("%d de %B de %Y")
        
        if date_str != previous_date:
            html_output += f'''
                <div class="date-header" style="text-align: center; margin: 20px 0;">
                    <strong>{formatted_date}</strong>
                </div>
            '''
            previous_date = date_str
        
        html_output += f'''
            <div class="message-box" style="margin: 10px 0; padding: 10px;">
                <div class="timestamp" style="color: #888; font-size: 0.9em;">
                    {time_str} - {sender}:
                </div>
                <div class="message-content">
                    {styled_message}
                </div>
            </div>
        '''
    return f'''
        <html>
        <head>
            <style>
                body {{ background-color: #333; color: white; font-family: Arial, sans-serif; }}
                .date-header {{ font-size: 1.2em; color: #AAAAAA; }}
                .message-box {{ background-color: inherit; }}  
                .timestamp {{ margin-bottom: 5px; }}
                .message-content {{ margin-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="chat-container">
                {html_output}
            </div>
        </body>
        </html>
    '''

def load_chats(directory="data/chats"):
    chats = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            chat_data = {
                "filename": filename,
                "nombre": os.path.splitext(filename)[0],
                "messages": []  # Almacenar mensajes en formato estructurado
            }
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as file:
                for line in file:
                    match = re.match(r'(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}) - ([^:]+): (.+)', line.strip())
                    if match:
                        date_str, time_str, sender, message = match.groups()
                        # Resaltar solo el mensaje
                        styled_message = highlight_keywords(message)
                        chat_data["messages"].append({
                            "date": date_str,
                            "time": time_str,
                            "sender": sender,
                            "message": styled_message
                        })
            chats.append(chat_data)
    return chats

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

def infer_date(text):
    today = datetime.now().date()
    if "mañana" in text.lower():
        return today + timedelta(days=1)
    elif "mes siguiente" in text.lower():
        next_month = today.replace(month=today.month + 1)
        return next_month if today.month < 12 else today.replace(year=today.year+1, month=1)
    elif "próximo" in text.lower():
        return today + timedelta(weeks=1)
    # Agregar más lógica para "pasado", "último día", etc.
    return today

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
