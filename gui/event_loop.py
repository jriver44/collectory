from PySide6.QtWidgets import QApplication, QWidget
import time

app = QApplication([])
win = QWidget()
win.setWindowTitle("Try Stalling the Loop")
win.show()

time.sleep(5)
print("This prints *after* the window appears")

app.exec()