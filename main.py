import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    print("Iniciando la aplicación...")  # Depuración

    app = QApplication(sys.argv)
    window = MainWindow()  # Crear la ventana principal
    window.show()  # Mostrar la ventana
    print("Ventana principal mostrada.")  # Depuración

    sys.exit(app.exec())  # Ejecutar la aplicación

if __name__ == "__main__":
    main()