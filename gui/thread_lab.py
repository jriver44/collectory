from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
import time

class Worker(QThread):
    finished = Signal(str)
    
    def run(self):
        time.sleep(5)
        self.finished.emit("Task complete!")

app = QApplication([])
win = QWidget()
win.setWindowTitle("Threading Basics Lab")

status = QLabel("Idle")
start_btn = QPushButton("Start Background Task")

layout = QVBoxLayout(win)
layout.addWidget(status)
layout.addWidget(start_btn)
win.setLayout(layout)

worker = Worker()
worker.finished.connect(lambda msg: status.setText(msg))

start_btn.clicked.connect(lambda: (status.setText("Working..."), worker.start()))

win.show()
app.exec()