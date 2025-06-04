import os
import re
import pandas as pd
import spacy

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
        r'\b(horario|hora|mañana|tarde|noche|cita|disponibilidad|nocturnidad)\b',  # Horario
        r'\b(ubicación|dirección|lugar|envío|localización)\b',  # Ubicación/envío
        r'\b(precio|tarifa|coste|valor|factura|pedido|importe)\b',  # Precio y facturación
        r'\b(urgente|importante|revisar|última|último)\b'  # Urgencia
    ]
    for pattern in patterns:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    return False

def load_chats(directory="data/chats"):
    chats = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            chat_data = {
                "filename": filename,
                "messages": []
            }
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as file:
                for line in file:
                    match = re.match(r"(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}) - (.*?): (.*)", line)
                    if match:
                        fecha, hora, sender, mensaje = match.groups()
                        chat_data["messages"].append({
                            "fecha": f"{fecha} {hora}",
                            "sender": sender,
                            "mensaje": mensaje
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