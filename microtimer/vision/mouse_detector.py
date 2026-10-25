from __future__ import annotations

import cv2
import numpy as np

from core.models import RoiBundle


class MouseDetector:
    def __init__(self, diff_threshold: int = 30, goal_ratio_threshold: float = 0.02, start_ratio_threshold: float = 0.05, finish_consecutive_frames: int = 3):
        self.diff_threshold = diff_threshold
        self.goal_ratio_threshold = goal_ratio_threshold
        self.start_ratio_threshold = start_ratio_threshold
        self.finish_consecutive_frames = finish_consecutive_frames
        
        self.start_bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=self.diff_threshold, detectShadows=False)
        self.goal_bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=self.diff_threshold, detectShadows=False)
        self.goal_hit_streak = 0
        self.start_hit_streak = 0
        self._frame_count = 0

    def reset(self) -> None:
        self.start_bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=self.diff_threshold, detectShadows=False)
        self.goal_bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=self.diff_threshold, detectShadows=False)
        self.goal_hit_streak = 0
        self.start_hit_streak = 0
        self._frame_count = 0

    def update(self, warped_frame: np.ndarray, rois: RoiBundle) -> tuple[bool, float, bool]:
        self._frame_count += 1
        gray = cv2.cvtColor(warped_frame, cv2.COLOR_BGR2GRAY)

        sx, sy, sw, sh = rois.start_line
        start_patch = gray[sy : sy + sh, sx : sx + sw]
        start_crossed = False
        if start_patch.size > 0:
            s_mask = self.start_bg_subtractor.apply(start_patch, learningRate=-1)
            _, s_mask = cv2.threshold(s_mask, 200, 255, cv2.THRESH_BINARY)
            s_ratio = float(np.count_nonzero(s_mask)) / float(s_mask.size)
            
            if s_ratio > self.start_ratio_threshold:
                self.start_hit_streak += 1
            else:
                self.start_hit_streak = max(0, self.start_hit_streak - 1)
            
            start_crossed = self.start_hit_streak >= 2

        gx, gy, gw, gh = rois.goal_area
        goal_patch = gray[gy : gy + gh, gx : gx + gw]
        if goal_patch.size == 0:
            return start_crossed, 0.0, False

        g_mask = self.goal_bg_subtractor.apply(goal_patch, learningRate=-1)
        _, g_mask = cv2.threshold(g_mask, 200, 255, cv2.THRESH_BINARY)
        changed_ratio = float(np.count_nonzero(g_mask)) / float(g_mask.size)

        if changed_ratio > self.goal_ratio_threshold:
            self.goal_hit_streak += 1
        else:
            self.goal_hit_streak = max(0, self.goal_hit_streak - 1)

        in_goal = self.goal_hit_streak >= self.finish_consecutive_frames
        
        # Ignore triggers for the first 10 frames to allow MOG2 to stabilize its background
        if self._frame_count < 10:
            start_crossed = False
            in_goal = False
            
        return start_crossed, changed_ratio, in_goal
