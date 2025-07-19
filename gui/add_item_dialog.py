from PySide6.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox,
    QLineEdit, QDoubleSpinBox, QVBoxLayout
)

class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add new item")
        
        self.name_edit = QLineEdit(self)
        self.name_edit.setPlaceholderText("Enter item name")
        
        self.cat_edit = QLineEdit(self)
        self.cat_edit.setPlaceholderText("Enter item's category")
        
        self.quan_edit = QDoubleSpinBox(self)
        self.quan_edit.setRange(0, 1_000_000)        

        form = QFormLayout()
        form.addRow("Name:", self.name_edit)
        form.addRow("Category:", self.cat_edit)
        form.addRow("Quantity:", self.quan_edit)
        
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )
        
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form)
        main_layout.addWidget(self.buttons)
        self.setLayout(main_layout)
        
    def data(self):
        return {
            "name": self.name_edit.text().strip(),
            "category": self.cat_edit.text().strip(),
            "quantity": int(self.quan_edit.value())
        }