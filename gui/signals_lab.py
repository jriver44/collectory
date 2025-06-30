from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
)

def on_click():
    label.setText("Updated via named function")

app = QApplication([])
win = QWidget()
win.setWindowTitle("Signals & Slots Lab")

label = QLabel("Click the button to change this text")
button = QPushButton("Press Me")

layout = QVBoxLayout(win)
layout.addWidget(label)
layout.addWidget(button)
win.setLayout(layout)

button.clicked.connect(on_click)

win.show()
app.exec()