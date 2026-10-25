from __future__ import annotations

import threading
import time
import logging
import cv2
from dataclasses import dataclass
from typing import Optional

from core.fsm import TimerFSM
from core.models import DetectionResult
from core.timing import elapsed_ms, now_s
from pipeline.shared_state import SharedFrameState
from vision.aruco_localizer import ArucoLocalizer
from vision.mouse_detector import MouseDetector
from vision.roi_builder import build_rois
from vision.warp import warp_to_map


@dataclass
class ProcessOutput:
    result: DetectionResult
    overlay_frame: Optional[object]
    fps: float


class ProcessWorker:
    def __init__(self, shared_state: SharedFrameState, config: dict, timer_fsm: TimerFSM):
        self.shared_state = shared_state
        self.config = config
        self.timer_fsm = timer_fsm
        proc = config.get("processing", {})
        self.map_size = (int(proc.get("map_width", 800)), int(proc.get("map_height", 800)))
        self.localizer = ArucoLocalizer(proc.get("aruco_dict", "DICT_4X4_50"), proc.get("corner_ids", [0, 1, 2, 3]))
        self.rois = build_rois(
            self.map_size,
            start_corner=proc.get("start_corner", "top_left"),
            start_line_thickness_pct=float(proc.get("start_line_thickness_pct", 0.03)),
            goal_size_pct=float(proc.get("goal_size_pct", 0.16)),
            inset_pct=float(proc.get("map_inset_pct", 0.0)),
        )
        self.detector = MouseDetector(
            diff_threshold=int(proc.get("diff_threshold", 30)),
            goal_ratio_threshold=float(proc.get("goal_ratio_threshold", 0.02)),
            finish_consecutive_frames=int(proc.get("finish_consecutive_frames", 3)),
        )
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.latest_output = ProcessOutput(result=DetectionResult(), overlay_frame=None, fps=0.0)
        self._last_state = self.timer_fsm.snapshot.state
        self._last_frame_index = -1
        self._fps_window_start_s = now_s()
        self._fps_window_count = 0
        self._fps_value = 0.0
        self._no_aruco_frame_size: tuple[int, int] | None = None
        self._rois_user_set: bool = False

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)

    def _run(self) -> None:
        while not self.stop_event.is_set():
            packet = None
            with self.shared_state.lock:
                if self.shared_state.latest is not None:
                    packet = self.shared_state.latest
            if packet is None:
                time.sleep(0.005)
                continue
            if packet.frame_index == self._last_frame_index:
                time.sleep(0.002)
                continue
            self._last_frame_index = packet.frame_index

            start_s = now_s()
            homography, markers_found = self.localizer.detect_map_homography(packet.frame, self.map_size)
            result = DetectionResult(markers_found=markers_found, rois=self.rois)
            overlay = None

            if homography is not None:
                warped = warp_to_map(packet.frame, homography, self.map_size)
                overlay = warped
            else:
                # No ArUco: use raw frame directly for both detection and display
                h_f, w_f = packet.frame.shape[:2]
                frame_size = (w_f, h_f)
                # Rebuild default ROIs to match camera frame size (skip if user set custom ROIs)
                if frame_size != self._no_aruco_frame_size and not self._rois_user_set:
                    self._no_aruco_frame_size = frame_size
                    proc = self.config.get("processing", {})
                    self.rois = build_rois(
                        frame_size,
                        start_corner=proc.get("start_corner", "top_left"),
                        start_line_thickness_pct=float(proc.get("start_line_thickness_pct", 0.03)),
                        goal_size_pct=float(proc.get("goal_size_pct", 0.16)),
                        inset_pct=float(proc.get("map_inset_pct", 0.0)),
                    )
                result.rois = self.rois
                warped = packet.frame
                overlay = packet.frame

            result.warped_frame = warped
            start_crossed, goal_ratio, in_goal = self.detector.update(warped, result.rois)
            result.start_crossed = start_crossed
            result.goal_changed_ratio = goal_ratio
            result.mouse_in_goal = in_goal
            if start_crossed:
                self.timer_fsm.on_start_trigger()
            if in_goal:
                self.timer_fsm.on_finish_trigger()

            snapshot = self.timer_fsm.tick()
            if snapshot.state != self._last_state:
                logging.info(
                    "state_transition from=%s to=%s frame=%s goal_ratio=%.4f markers=%s",
                    self._last_state.value,
                    snapshot.state.value,
                    packet.frame_index,
                    result.goal_changed_ratio,
                    result.markers_found,
                )
                if snapshot.state.value == "FINISHED":
                    logging.info("run_finished elapsed_ms=%.3f", snapshot.elapsed_s * 1000.0)
                self._last_state = snapshot.state
            end_s = now_s()
            result.latency_ms = elapsed_ms(start_s, end_s)

            self._fps_window_count += 1
            window_elapsed = end_s - self._fps_window_start_s
            if window_elapsed >= 0.5:
                self._fps_value = self._fps_window_count / max(window_elapsed, 1e-6)
                self._fps_window_start_s = end_s
                self._fps_window_count = 0

            self.latest_output = ProcessOutput(result=result, overlay_frame=overlay, fps=self._fps_value)
