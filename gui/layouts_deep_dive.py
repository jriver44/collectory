from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout
)

app = QApplication([])

win = QWidget()
win.setWindowTitle("Layouts Deep Dive")

outer = QVBoxLayout(win)

hbox = QHBoxLayout()
hbox.addWidget(QPushButton("One"))
hbox.addWidget(QPushButton("Two"))
hbox.addWidget(QPushButton("Three"))
outer.addLayout(hbox)

grid = QGridLayout()
grid.addWidget(QLabel("First Name:"), 0, 0)
grid.addWidget(QLineEdit(), 0, 1)
grid.addWidget(QLabel("Last Name:"), 1, 0)
grid.addWidget(QLineEdit(), 1, 1)
outer.addLayout(grid)

btn_row = QHBoxLayout()
btn_row.addStretch(1)
btn_row.addWidget(QPushButton("Submit"))
outer.addLayout(btn_row)

win.show()
app.exec()