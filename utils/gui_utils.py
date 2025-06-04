# utils/gui_utils.py
import os
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from utils.styles import BUTTON_STYLE, ICON_DIR 

def create_button(text, icon_name, callback, fixed_size=(120, 40)):
    btn = QPushButton(text)
    btn.setIcon(QIcon(os.path.join(ICON_DIR, icon_name)))
    btn.setStyleSheet(BUTTON_STYLE)
    btn.setFixedSize(*fixed_size)
    btn.clicked.connect(callback)
    return btn