from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox,
    QLineEdit, QDoubleSpinBox, QVBoxLayout
)

class AddItemDialog(QDialog):
    """Model dialog for creating a new item (GUI).
    
    Responsibilities
    -----------------
        - Collect user input for 'name', 'category', and 'quantity'.
        - Validate minimally at the widget level (non-empty text is not enforced here).
        - Expose a 'data()' helper that returns a normalized dict.
        
    Relationships
    -------------
        - Typicallly invoked by the main window/controller to gather input.
        - The reutnred dict is compatible with domain functions like 'create_new_item'.
        
    Thread/UI
    ---------
        - Must be created and used on the Qt GUI thread.
        - Model by default, blocks the claler until accepted/rejected.
    """
    def __init__(self, parent=None):
        """Initialize child widgets and lay out the form.
        
        Args:
            parents: Optional Qt parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Add new item")
        
        # -- Inputs -----------------------------------------------------
        self.name_edit = QLineEdit(self)
        self.name_edit.setPlaceholderText("Enter item name")
        
        self.cat_edit = QLineEdit(self)
        self.cat_edit.setPlaceholderText("Enter item's category")
        
        self.quan_edit = QDoubleSpinBox(self)
        self.quan_edit.setRange(0, 1_000_000)        

        # -- Form layout ---------------------------------------------------
        form = QFormLayout()
        form.addRow("Name:", self.name_edit)
        form.addRow("Category:", self.cat_edit)
        form.addRow("Quantity:", self.quan_edit)
        
        # -- Dialog buttons- --------------------------------------------------
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self
        )
        
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        # -- Main layout ----------------------------------------------
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form)
        main_layout.addWidget(self.buttons)
        self.setLayout(main_layout)
        
    def data(self):
        """Return normalized item fields collected from the form.
        
        Returns:
            dict: a mapping with keys:
                - name: trimmed String
                - category: trimmed String
                - quantity: integer quantity derived from the spinbox value.
        """
        return {
            "name": self.name_edit.text().strip(),
            "category": self.cat_edit.text().strip(),
            "quantity": int(self.quan_edit.value())
        }