import os
COMPANY_EMAIL_ADDRESS = None
COOP_EMAIL_ADDRESS = None
EMAIL_ADDRESS = "relatifvision@gmail.com"
SERVICE_ACCOUNT_FILE = './calendar_api_setting/service-account-file.json'
APP_PASSWORD = "gynw zjsa uina vbix"
SMTP_SERVER = 'smtp.gmail.com'
# SMTP_PORT = 587
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
EXCEL_FILE_PATH = 'data/db.xlsx'
CALENDAR_ID = 'ce8dfca9b4f4a898433e722e3d6008a6f6413ad3f334a04a19809f7074261fe5@group.calendar.google.com'
SMTP_PORT = 465

CREDENTIALS_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 
        './calendar_api_setting/credentials.json'
    )
)
TOKEN_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 
        'token.json'
    )
)

ICON_DIR = os.path.join(os.path.dirname(__file__), 'data', 'icon')

# Opciones de tareas
TASK_OPTIONS = [
    "Técnico de Video",
    "Técnico de Iluminación",
    "Técnico pantalla Led",
    "Técnico de Streaming",
    "VideoMapping",
    "LedMapping",
    "Técnico Iluminación y Video",
    "Técnico Iluminación, Video y Sónido"
]