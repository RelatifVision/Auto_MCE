# utils/whatsapp_utils.py
import os
from PyQt6.QtWidgets import QListWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from utils.common_functions import show_info_dialog, show_error_dialog
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

def update_chat_content(main_window, current_item, list_widget):
    if current_item:
        selected_chat_name = current_item.text()
        for chat in main_window.chats:
            if chat["nombre"] == selected_chat_name:
                # Pasar solo los mensajes, no todo el chat
                formatted_chat = process_chat(chat["messages"])  
                main_window.chat_content.setHtml(formatted_chat)  
                break

def send_wpp(main_window):
    message = main_window.message_input.toPlainText()
    selected_chat = main_window.chat_list_send.currentItem()
    destinatario = selected_chat.text() if selected_chat else "Sin destinatario"
    attached_files = getattr(main_window, "attached_files", [])  # <--- Lee desde attached_files
    
    message_text = f"El mensaje:\n\n{message}"
    
    if attached_files:
        files_str = "\n\nArchivos adjuntos:\n- " + "\n- ".join(attached_files)
        message_text += files_str
    
    message_text += f"\n\nSerá enviado a '{destinatario}' por WhatsApp.\n\nAPIs de Meta no están disponibles."
    
    show_info_dialog(main_window, "Éxito", message_text)
    
def confirm_wpp(main_window):
    main_window.message_input.setText(
        "Okey, podré asistir a las fechas indicadas, contar conmigo"
    )

def reject_wpp(main_window):
    main_window.message_input.setText(
        "Lamentablemente no tendré disponibilidad para esas fechas, pero deseo colaborar más adelante"
    )
    
def clear_whatsapp_message(chat_list, compose_area, attach_list):
    chat_list.setCurrentRow(-1)
    compose_area.clear()
    attach_list.clear()