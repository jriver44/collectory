from PySide6.QtWidgets import QApplication, QWidget, QPushButton

app = QApplication([])
parent = QWidget()
parent.setWindowTitle("Parent Window")
parent.setGeometry(100, 100, 300, 200)

child_btn = QPushButton("I'm a child", parent)
child_btn.move(50, 50)

orphan = QPushButton("Orphan")
orphan.setParent(parent)
orphan.move(100, 100)

parent.show()
orphan.show()
app.exec()