from __future__ import annotations

import cv2
import numpy as np


def warp_to_map(frame: np.ndarray, homography: np.ndarray, map_size: tuple[int, int]) -> np.ndarray:
    width, height = map_size
    return cv2.warpPerspective(frame, homography, (width, height))
