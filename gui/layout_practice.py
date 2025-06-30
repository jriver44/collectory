from PySide6.QtWidgets import (
    QApplication, QWidget,
    QPushButton, QLabel, QLineEdit,
    QHBoxLayout, QGridLayout
)

app = QApplication([])

hwin = QWidget()
hwin.setWindowTitle("HBoxLayout Example")
hbox = QHBoxLayout(hwin)

hbox.addWidget(QPushButton("One"))
hbox.addWidget(QPushButton("Two"))
hbox.addWidget(QPushButton("Three"))

hwin.setLayout(hbox)
hwin.show()

gwin = QWidget()
gwin.setWindowTitle("GridLayout Example")
grid = QGridLayout(gwin)

grid.addWidget(QLabel("Name:"), 0, 0)
grid.addWidget(QLineEdit(), 0, 1)

grid.addWidget(QLabel("Quantity:"), 1, 0)
grid.addWidget(QLineEdit(), 1, 1)

big_btn = QPushButton("BigButton")
grid.addWidget(big_btn, 2, 0, 1, 2)

gwin.setLayout(grid)
gwin.show()

app.exec()