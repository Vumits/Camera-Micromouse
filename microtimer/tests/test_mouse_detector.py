import numpy as np

from vision.mouse_detector import MouseDetector
from vision.roi_builder import build_rois


def test_mouse_detector_goal_diff():
    detector = MouseDetector(diff_threshold=10, goal_ratio_threshold=0.01, finish_consecutive_frames=1)
    rois = build_rois((100, 100))

    frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
    frame2 = frame1.copy()
    gx, gy, gw, gh = rois.goal_area
    frame2[gy : gy + gh, gx : gx + gw] = 255

    detector.update(frame1, rois)
    _, ratio, in_goal = detector.update(frame2, rois)
    assert ratio > 0.01
    assert in_goal
