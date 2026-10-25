from __future__ import annotations

from PyQt6 import QtWidgets


class ControlPanel(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        form = QtWidgets.QFormLayout()
        self.team_name_edit = QtWidgets.QLineEdit()
        self.team_name_edit.setPlaceholderText("Team name")
        self.duration_spin = QtWidgets.QSpinBox()
        self.duration_spin.setRange(1, 180)
        self.duration_spin.setValue(10)
        
        form.addRow("Team:", self.team_name_edit)
        form.addRow("Minutes:", self.duration_spin)

        grid = QtWidgets.QGridLayout()
        self.start_session_btn = QtWidgets.QPushButton("Start Session")
        self.stop_session_btn = QtWidgets.QPushButton("Stop Session")
        
        self.arm_btn = QtWidgets.QPushButton("Arm")
        self.reset_btn = QtWidgets.QPushButton("Reset")
        self.next_run_btn = QtWidgets.QPushButton("Next Run")
        self.reset_rois_btn = QtWidgets.QPushButton("Reset ROIs")
        
        # Row 0: Session controls
        grid.addWidget(self.start_session_btn, 0, 0)
        grid.addWidget(self.stop_session_btn, 0, 1)
        # Row 1: Timer controls
        grid.addWidget(self.arm_btn, 1, 0)
        grid.addWidget(self.reset_btn, 1, 1)
        # Row 2: Run / ROIs
        grid.addWidget(self.next_run_btn, 2, 0)
        grid.addWidget(self.reset_rois_btn, 2, 1)

        layout.addLayout(form)
        layout.addLayout(grid)
