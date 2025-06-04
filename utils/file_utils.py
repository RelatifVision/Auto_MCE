from PyQt6.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem, QListWidget
from PyQt6.QtCore import Qt
import os

def select_files(parent, allowed_types=None, attach_list=None):
    """
    Abre un diálogo para seleccionar archivos con filtros predefinidos.
    
    Args:
        parent (QWidget): Ventana principal para el diálogo.
        allowed_types (list, optional): Lista de tipos de archivo (ej: ["Word", "PDF"]). 
            Por defecto, todos los tipos soportados.
    
    Returns:
        list: Rutas absolutas de los archivos seleccionados.
    """
   
    filters = {
        "Word": "Word Files (*.doc *.docx)",
        "PowerPoint": "PowerPoint Files (*.ppt *.pptx)",
        "PDF": "PDF Files (*.pdf)",
        "Images": "Image Files (*.png *.jpg *.jpeg)",
        "Videos": "Video Files (*.mp4 *.avi)",
        "Excel": "Excel Files (*.xls *.xlsx)",
        "PNG": "PNG Files (*.png)",
        "All": "All Files (*)"
    }

    if allowed_types is None:
        allowed_types = ["All"]
    
   
    file_filter = ";;".join([filters[t] for t in allowed_types])
    file_filter += ";;All Files (*)" 
    
   
    file_paths, _ = QFileDialog.getOpenFileNames(
        parent,
        "Adjuntar archivos",
        os.path.expanduser("~"),  
        file_filter
    )
    
    # Almacenar las rutas completas en attached_files
    if hasattr(parent, "attached_files"):
        parent.attached_files = file_paths
    else:
        parent.attached_files = []
    # Mostrar solo los nombres en la lista
    if attach_list is not None:
        #attach_list.clear()
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            item = QListWidgetItem(file_name, attach_list)
    return file_paths

def clear_whatsapp_message(compose_area, destination_input, attach_list=None):
    """
    Limpia área de mensaje, destinatario y adjuntos (si existen).
    """
    compose_area.clear()
    destination_input.clear()
    if attach_list:
        attach_list.clear()
        if hasattr(compose_area.parent(), "attached_files"):
            compose_area.parent().attached_files = []