from __future__ import annotations

from PyQt6 import QtWidgets, QtCore


class StatusPanel(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("QLabel { font-size: 9pt; font-weight: bold; }")

        self.countdown_label = QtWidgets.QLabel("00:00")
        self.countdown_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setMinimumHeight(110)
        self.countdown_label.setStyleSheet("color: white; background-color: #d32f2f; border-radius: 8px; padding: 5px; margin-bottom: 15px; font-size: 54pt; font-weight: bold;")
        layout.addWidget(self.countdown_label)

        self.elapsed_label = QtWidgets.QLabel("0.000 s")
        self.elapsed_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.elapsed_label.setMinimumHeight(110)
        self.elapsed_label.setStyleSheet("color: white; background-color: #388E3C; border-radius: 8px; padding: 5px; margin-bottom: 15px; font-size: 54pt; font-weight: bold;")
        layout.addWidget(self.elapsed_label)

        top = QtWidgets.QFormLayout()
        top.setVerticalSpacing(8)
        self.state_label = QtWidgets.QLabel("IDLE")
        self.team_label = QtWidgets.QLabel("-")
        self.best_label = QtWidgets.QLabel("-")
        self.run_count_label = QtWidgets.QLabel("0")
        top.addRow("State", self.state_label)
        top.addRow("Team", self.team_label)
        top.addRow("Best", self.best_label)
        top.addRow("Runs", self.run_count_label)

        self.run_list = QtWidgets.QListWidget()
        self.run_list.setMinimumHeight(40)
        self.run_list.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addLayout(top)
        layout.addWidget(QtWidgets.QLabel("Run times"))
        layout.addWidget(self.run_list)
