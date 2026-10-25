from __future__ import annotations

import cv2
import numpy as np

from core.models import DetectionResult, TimerState


def draw_overlay(frame: np.ndarray, result: DetectionResult, state: TimerState, elapsed_s: float) -> np.ndarray:
    out = frame.copy()
    if result.rois:
        sx, sy, sw, sh = result.rois.start_line
        gx, gy, gw, gh = result.rois.goal_area
        cv2.rectangle(out, (sx, sy), (sx + sw, sy + sh), (255, 200, 0), 2)
        cv2.rectangle(out, (gx, gy), (gx + gw, gy + gh), (0, 255, 255), 2)

    cv2.putText(out, f"State: {state.value}", (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(out, f"Elapsed: {elapsed_s:.3f}s", (12, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(out, f"Markers: {result.markers_found}", (12, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(out, f"GoalRatio: {result.goal_changed_ratio:.4f}", (12, 108), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    return out
