import pytest
from PyQt6.QtWidgets import QApplication
from ui.mail_window import mailWindow

@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    window = EmailWindow()
    qtbot.addWidget(window)
    return window

def test_initialization(app):
    assert app.windowTitle() == "Gestión Email"
    assert app.geometry().width() == 800
    assert app.geometry().height() == 600
    assert app.received_messages_area.toPlainText() == ""
    assert app.asunto_input.text() == ""
    assert app.destination_input.text() == ""
    assert app.compose_area.toPlainText() == ""

def test_send_email(app, qtbot, capsys):
    app.asunto_input.setText("Test Asunto")
    app.destination_input.setText("test@example.com")
    app.compose_area.setPlainText("Test Message")
    qtbot.mouseClick(app.btn_send, qtbot.LeftButton)
    captured = capsys.readouterr()
    assert "Enviando correo a Test Asunto:\ntest@example.com:\nTest Message" in captured.out

def test_clear_compose_area(app, qtbot):
    app.asunto_input.setText("Test Asunto")
    app.destination_input.setText("test@example.com")
    app.compose_area.setPlainText("Test Message")
    qtbot.mouseClick(app.btn_clear, qtbot.LeftButton)
    assert app.asunto_input.text() == ""
    assert app.destination_input.text() == ""
    assert app.compose_area.toPlainText() == ""

def test_save_email(app, qtbot, capsys):
    app.asunto_input.setText("Test Asunto")
    app.destination_input.setText("test@example.com")
    app.compose_area.setPlainText("Test Message")
    qtbot.mouseClick(app.btn_save, qtbot.LeftButton)
    captured = capsys.readouterr()
    assert "Guardando correo a Test Asunto:\ntest@example.com:\nTest Message" in captured.out

def test_set_auto_text(app):
    app.set_auto_text("Dar alta S.S.", "Necesito que me deis de alta los días, un saludo y muchas gracias")
    assert app.asunto_input.text() == "Alta en Seguridad Social"
    assert app.destination_input.text() == "seguridad.social@example.com"
    assert app.compose_area.toPlainText() == "Necesito que me deis de alta los días, un saludo y muchas gracias"

    app.set_auto_text("Pedir Factura", "Datos del cliente, importe total + IVA, concepto de la empresa cliente")
    assert app.asunto_input.text() == "Solicitud de Factura"
    assert app.destination_input.text() == "facturacion@example.com"
    assert app.compose_area.toPlainText() == "Datos del cliente, importe total + IVA, concepto de la empresa cliente"

    app.set_auto_text("Enviar Factura", "Para las fechas, con x horarios para tal evento y ubicación, como técnico de video y adjuntamos la factura indicamos precio total e indicamos concepto de la cooperativa al cliente")
    assert app.asunto_input.text() == "Envío de Factura"
    assert app.destination_input.text() == "cliente@example.com"
    assert app.compose_area.toPlainText() == "Para las fechas, con x horarios para tal evento y ubicación, como técnico de video y adjuntamos la factura indicamos precio total e indicamos concepto de la cooperativa al cliente"