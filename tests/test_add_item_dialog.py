import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialogButtonBox, QDialog
from gui.add_item_dialog import AddItemDialog

def test_add_item_dialog_fields_and_data(qtbot):
    dlg = AddItemDialog()
    qtbot.addWidget(dlg)
    
    dlg.name_edit.setText("My Collection Item")
    dlg.cat_edit.setText("Rare Category")
    dlg.quan_edit.setValue(42)
    
    ok_btn = dlg.buttons.button(QDialogButtonBox.Ok)
    qtbot.mouseClick(ok_btn, Qt.LeftButton)
    
    assert dlg.result() == QDialog.Accepted    
    data = dlg.data()
    assert data["name"] == "My Collection Item"
    assert data["category"] == "Rare Category"
    assert data["quantity"] == 42