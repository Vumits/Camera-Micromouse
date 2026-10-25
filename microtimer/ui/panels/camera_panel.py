from __future__ import annotations

from PyQt6 import QtCore, QtGui, QtWidgets


class CameraPanel(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        form = QtWidgets.QFormLayout()
        self.source_combo = QtWidgets.QComboBox()
        self.source_combo.addItems(["usb", "ip"])
        self.input_edit = QtWidgets.QLineEdit("0")
        
        form.addRow("Source:", self.source_combo)
        form.addRow("Index/URL:", self.input_edit)

        btn_layout = QtWidgets.QHBoxLayout()
        self.connect_btn = QtWidgets.QPushButton("Connect")
        self.disconnect_btn = QtWidgets.QPushButton("Disconnect")
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.disconnect_btn)

        layout.addLayout(form)
        layout.addLayout(btn_layout)
