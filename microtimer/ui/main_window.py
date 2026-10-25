from __future__ import annotations

from pathlib import Path

from PyQt6 import QtCore, QtGui, QtWidgets

from core.competition import CompetitionSession
from core.fsm import TimerFSM
from pipeline.capture_worker import CaptureWorker
from pipeline.process_worker import ProcessWorker
from pipeline.shared_state import SharedFrameState
from ui.panels.camera_panel import CameraPanel
from ui.panels.control_panel import ControlPanel
from ui.panels.status_panel import StatusPanel
from ui.viewmodels.app_vm import AppViewModel
from ui.components.interactive_label import InteractiveLabel
from vision.camera.factory import build_camera_source
from vision.overlay import draw_overlay


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self.setWindowTitle("Micromouse Timer")
        self.resize(1100, 700)
        self.config = config
        self.timer_fsm = TimerFSM(
            debounce_ms=int(config.get("processing", {}).get("debounce_ms", 80)),
            min_run_ms=200,
        )
        self.vm = AppViewModel(self.timer_fsm)
        self.shared_state = SharedFrameState()
        self.capture_worker: CaptureWorker | None = None
        self.process_worker: ProcessWorker | None = None
        self.camera = None
        self.competition = CompetitionSession()
        self._last_fsm_state = self.timer_fsm.snapshot.state
        self.saved_rois = None

        central = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Video Preview (Left)
        self.preview_label = InteractiveLabel("No frame")
        main_layout.addWidget(self.preview_label, stretch=5)
        self.preview_label.roi_updated.connect(self.on_roi_updated)

        # Sidebar (Right)
        sidebar = QtWidgets.QWidget()
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 0, 0, 0)
        sidebar_layout.setSpacing(5)

        self.camera_panel = CameraPanel()
        self.control_panel = ControlPanel()
        self.status_panel = StatusPanel()

        cam_group = QtWidgets.QGroupBox("Camera")
        cam_group.setMaximumHeight(120)
        cam_layout = QtWidgets.QVBoxLayout(cam_group)
        cam_layout.setContentsMargins(5, 15, 5, 5)
        cam_layout.addWidget(self.camera_panel)

        ctrl_group = QtWidgets.QGroupBox("Controls")
        ctrl_group.setMaximumHeight(160)
        ctrl_layout = QtWidgets.QVBoxLayout(ctrl_group)
        ctrl_layout.setContentsMargins(5, 15, 5, 5)
        ctrl_layout.addWidget(self.control_panel)

        stat_group = QtWidgets.QGroupBox("Status")
        stat_layout = QtWidgets.QVBoxLayout(stat_group)
        stat_layout.addWidget(self.status_panel)

        sidebar_layout.addWidget(cam_group, stretch=0)
        sidebar_layout.addWidget(ctrl_group, stretch=0)
        sidebar_layout.addWidget(stat_group, stretch=1)

        main_layout.addWidget(sidebar)
        self.setCentralWidget(central)

        # Apply Light Theme
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QWidget { color: #222222; font-family: Arial, sans-serif; font-size: 10pt; }
            QGroupBox { font-weight: bold; border: 1px solid #cccccc; border-radius: 6px; margin-top: 15px; padding-top: 15px; background-color: #fafafa; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
            QLineEdit, QSpinBox, QComboBox, QListWidget { background-color: #ffffff; border: 1px solid #cccccc; border-radius: 4px; padding: 4px; color: #000000; }
            QComboBox QAbstractItemView { background-color: #ffffff; color: #000000; selection-background-color: #4CAF50; selection-color: #ffffff; }
            QPushButton { background-color: #e0e0e0; border: 1px solid #bcbcbc; border-radius: 4px; padding: 6px 12px; font-weight: bold; }
            QPushButton:hover { background-color: #d5d5d5; }
            QPushButton:pressed { background-color: #4CAF50; color: #ffffff; border: 1px solid #388E3C; }
            QLabel { background: transparent; }
        """)

        self.camera_panel.connect_btn.clicked.connect(self.on_connect)
        self.camera_panel.disconnect_btn.clicked.connect(self.on_disconnect)
        self.control_panel.arm_btn.clicked.connect(self.timer_fsm.arm)
        self.control_panel.reset_btn.clicked.connect(self.on_reset)
        self.control_panel.next_run_btn.clicked.connect(self.on_next_run)
        self.control_panel.start_session_btn.clicked.connect(self.on_start_session)
        self.control_panel.stop_session_btn.clicked.connect(self.on_stop_session)
        self.control_panel.reset_rois_btn.clicked.connect(self.on_reset_rois)

        self.ui_timer = QtCore.QTimer(self)
        self.ui_timer.timeout.connect(self.on_ui_tick)
        self.ui_timer.start(33)

    def on_roi_updated(self, mode: str, rect: tuple[int, int, int, int]) -> None:
        if self.competition.active:
            # Ignore edits during an active competition match
            return
        if not self.process_worker:
            return
            
        with self.shared_state.lock:
            if mode == "start":
                self.process_worker.rois.start_line = rect
            elif mode == "goal":
                self.process_worker.rois.goal_area = rect
            
            # Persist custom ROIs across camera reconnects
            self.saved_rois = self.process_worker.rois
            self.process_worker._rois_user_set = True

    def on_connect(self) -> None:
        self.on_disconnect()
        source_type = self.camera_panel.source_combo.currentText().strip()
        text = self.camera_panel.input_edit.text().strip()
        self.config.setdefault("camera", {})
        self.config["camera"]["source_type"] = source_type
        if source_type == "ip":
            self.config["camera"]["ip_url"] = text
        else:
            self.config["camera"]["usb_index"] = int(text) if text.isdigit() else 0

        self.camera = build_camera_source(self.config)
        self.capture_worker = CaptureWorker(self.camera, self.shared_state)
        self.process_worker = ProcessWorker(self.shared_state, self.config, self.timer_fsm)
        
        if self.saved_rois is not None:
            self.process_worker.rois = self.saved_rois
            self.process_worker._rois_user_set = True
            
        self.capture_worker.start()
        self.process_worker.start()

    def on_disconnect(self) -> None:
        if self.capture_worker:
            self.capture_worker.stop()
        if self.process_worker:
            self.process_worker.stop()
        if self.camera:
            self.camera.release()

    def on_reset(self) -> None:
        self.timer_fsm.reset()
        if self.process_worker:
            self.process_worker.detector.reset()

    def on_next_run(self) -> None:
        self.on_reset()
        self.timer_fsm.arm()

    def on_start_session(self) -> None:
        team = self.control_panel.team_name_edit.text().strip()
        minutes = int(self.control_panel.duration_spin.value())
        self.competition.start(team_name=team, duration_minutes=minutes)
        self.status_panel.run_list.clear()
        self.timer_fsm.reset()
        if self.process_worker:
            self.process_worker.detector.reset()

    def on_stop_session(self) -> None:
        if self.competition.active:
            self.competition.stop()
            if not self.competition.export_done:
                self._export_results()

    def on_reset_rois(self) -> None:
        if self.competition.active:
            # Ignore edits during an active competition match
            return
            
        self.saved_rois = None
        
        # Hot-reload the config so changes to default.yaml apply instantly 
        try:
            from app.config_loader import load_config
            new_cfg = load_config(Path("config/default.yaml"))
            self.config.update(new_cfg)
        except Exception:
            pass

        if self.process_worker:
            from vision.roi_builder import build_rois
            proc = self.config.get("processing", {})
            map_size = (int(proc.get("map_width", 800)), int(proc.get("map_height", 800)))
            fresh_rois = build_rois(
                map_size,
                start_corner=proc.get("start_corner", "top_left"),
                start_line_thickness_pct=float(proc.get("start_line_thickness_pct", 0.03)),
                goal_size_pct=float(proc.get("goal_size_pct", 0.16)),
                inset_pct=float(proc.get("map_inset_pct", 0.0)),
            )
            with self.shared_state.lock:
                self.process_worker.rois = fresh_rois
                self.process_worker._rois_user_set = False
                self.process_worker._no_aruco_frame_size = None

    def _format_mmss(self, seconds: float) -> str:
        total = int(max(0, seconds))
        mm = total // 60
        ss = total % 60
        return f"{mm:02d}:{ss:02d}"

    def _export_results(self) -> None:
        output_path = self.competition.export_excel(Path("exports"))
        QtWidgets.QMessageBox.information(
            self,
            "Competition ended",
            f"Time is up. Exported results:\n{output_path}",
        )

    def on_ui_tick(self) -> None:
        if not self.process_worker:
            return
        out = self.process_worker.latest_output
        self.vm.update_from_process(out.result, out.fps)
        snap = self.timer_fsm.tick()

        frame_to_show = None
        is_warped = False
        if out.overlay_frame is not None:
            frame_to_show = draw_overlay(out.overlay_frame, out.result, snap.state, snap.elapsed_s)
            is_warped = True
        else:
            with self.shared_state.lock:
                if self.shared_state.latest is not None:
                    frame_to_show = self.shared_state.latest.frame
        if frame_to_show is not None:
            self.preview_label.set_frame(frame_to_show, is_warped=is_warped)

        if self.competition.active and self._last_fsm_state != snap.state and snap.state.value == "FINISHED":
            run_no = self.competition.add_run(snap.elapsed_s)
            self.status_panel.run_list.addItem(f"Run {run_no}: {snap.elapsed_s:.3f} s")
        self._last_fsm_state = snap.state

        if self.competition.active:
            remaining = self.competition.remaining_seconds()
            self.status_panel.countdown_label.setText(self._format_mmss(remaining))
            if self.competition.is_time_up():
                self.competition.stop()
                if not self.competition.export_done:
                    self._export_results()
        else:
            self.status_panel.countdown_label.setText("00:00")

        best = self.competition.best_time_s()
        self.status_panel.team_label.setText(self.competition.team_name or "-")
        self.status_panel.best_label.setText("-" if best is None else f"{best:.3f} s")
        self.status_panel.run_count_label.setText(str(len(self.competition.runs)))

        self.status_panel.state_label.setText(snap.state.value)
        self.status_panel.elapsed_label.setText(f"{snap.elapsed_s:.3f} s")

    def closeEvent(self, event) -> None:
        self.on_disconnect()
        super().closeEvent(event)
