import smtplib
import base64
import imaplib
import os
import email
from email import message_from_bytes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header  
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import EMAIL_ADDRESS, APP_PASSWORD, SMTP_SERVER, SMTP_PORT, IMAP_SERVER

SCOPES = [
    'https://www.googleapis.com/auth/gmail.compose', 
    'https://www.googleapis.com/auth/gmail.readonly' 
]

def send_email(subject, recipient, body):
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = EMAIL_ADDRESS
    message['To'] = recipient
    message.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, APP_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient, message.as_string())
        return True, "Correo enviado exitosamente"
    except Exception as e:
        return False, f"Error SMTP: {str(e)}"

def save_draft(subject, recipient, body):
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = EMAIL_ADDRESS
    message['To'] = recipient
    message.attach(MIMEText(body, "plain"))
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        creds = _get_google_credentials()
        service = build('gmail', 'v1', credentials=creds)
        draft = service.users().drafts().create(userId='me', body={'message': {'raw': raw_message}}).execute()
        return True, f"Borrador guardado con ID: {draft['id']}"
    except Exception as e:
        return False, f"Error al guardar borrador: {str(e)}"

def load_inbox(mail_connection, LIMIT=5):
    try:
        mail_connection.select("inbox")
        status, messages = mail_connection.search(None, "ALL")
        if status != "OK":
            return []
        
        mail_ids = messages[0].split()
        if not mail_ids:
            return []
        
        if len(mail_ids) > LIMIT:
            mail_ids = mail_ids[-LIMIT:]  
            return process_messages(mail_connection, mail_ids)
    except Exception as e:
        print(f"Error al cargar mensajes recibidos: {e}")
        return []

def process_messages(mail_connection, mail_ids):
    messages = []
    for num in mail_ids:
        _, msg_data = mail_connection.fetch(num, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
                from_email = msg.get("From")
                messages.append(f"De: {from_email}\nAsunto: {subject}")
    return messages

def get_mail_connection():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ADDRESS, APP_PASSWORD)
    return mail

def load_drafts(mail_connection, LIMIT=10):
    try:
        mail_connection.select('[Gmail]/Borradores')
        status, messages = mail_connection.search(None, "ALL")
        if status != "OK":
            return []
        
        mail_ids = messages[0].split()  
        if not mail_ids:
            return []
        
        if len(mail_ids) > LIMIT:
            mail_ids = mail_ids[-LIMIT:]  
        return process_emails(mail_connection, mail_ids)
    except Exception as e:
        print(f"Error al cargar borradores: {str(e)}")
        return []

def process_emails(mail_connection, mail_ids):
    messages = []
    for num in mail_ids:
        _, msg_data = mail_connection.fetch(num, "(RFC822)")
        for part in msg_data:
            if isinstance(part, tuple):
                msg = message_from_bytes(part[1])
                subject, _ = decode_header(msg["Subject"])[0]
                subject = subject.decode() if isinstance(subject, bytes) else subject
                from_email = msg.get("From")
                messages.append(f"De: {from_email}\nAsunto: {subject}")
    return messages

def clear_mail_message(subject_input, destination_input, compose_area, attach_list):
    subject_input.clear()
    destination_input.clear()
    compose_area.clear()
    attach_list.clear()

def _get_google_credentials():
    token_path = 'token.json'
    credentials_path = 'calendar_api_setting/credentials.json'
    creds = None
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds