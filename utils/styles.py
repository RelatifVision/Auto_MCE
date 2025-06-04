import os

BUTTON_STYLE = """
    QPushButton {
        background-color: rgb(45, 45, 45); 
        color: #ffffff;
        border: 2px solid #111111;
        border-radius: 5px;
        padding: 10px;
    }
    QPushButton:hover {
        background-color: rgb(220, 220, 220); 
        color: #000000;
    }
"""

ICON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/icon"))