
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("PyQt6 Hello World - Dechen Choden")
window.setGeometry(300, 200, 400, 250)

heading = QLabel("Welcome to PyQt6!")
heading.setStyleSheet(
    "font-size: 22px; font-weight: bold;"
)

button = QPushButton("Click Me")

def show_message():
    QMessageBox.information(
        window,
        "Message",
        "Button Clicked!"
    )

button.clicked.connect(show_message)

layout = QVBoxLayout()
layout.addWidget(heading)
layout.addWidget(button)

window.setLayout(layout)

window.show()

sys.exit(app.exec())
