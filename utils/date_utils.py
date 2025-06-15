# utils/date_utils.py
from datetime import datetime, timedelta
import dateparser
from dateparser import parse
import re
from models.chat_parser import nlp

def infer_date(text):
    """Inferir fecha solo del cuerpo del mensaje."""
    doc = nlp(text)
    today = datetime.now().date()
    
    # 1. Detectar fechas por entidad (spaCy)
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            try:
                # Intentar múltiples formatos
                date_str = ent.text
                parsed_date = parse(date_str, languages=['es'])
                if parsed_date:
                    return parsed_date.date()
            except Exception as e:
                pass  # Ignorar errores de formato
    
    # 2. Lógica tradicional con palabras clave
    if "mañana" in text.lower():
        return today + timedelta(days=1)
    elif "próximo" in text.lower():
        return today + timedelta(weeks=1)
    elif "dentro de" in text.lower():
        # Ejemplo: "dentro de 3 días"
        match = re.search(r'\d+', text)
        if match:
            days = int(match.group())
            return today + timedelta(days=days)
    
    # 3. Uso de dateparser para fechas complejas
    date_str = parse(text, languages=['es'])
    if date_str:
        return date_str.date()
    
    # 4. Devolver fecha actual si no se detecta nada
    return today