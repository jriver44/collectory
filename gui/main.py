from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton

app = QApplication([])

window = QWidget()
window.setWindowTitle("Curation")

layout = QVBoxLayout(window)

label = QLabel("Hello, Curration!")
layout.addWidget(label)

button = QPushButton("Update Greeting")
layout.addWidget(button)

button.clicked.connect(lambda: label.setText("You clicked the button!"))


window.show()

app.exec()