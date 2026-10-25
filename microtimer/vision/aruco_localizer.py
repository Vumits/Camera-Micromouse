from __future__ import annotations

import cv2
import numpy as np


ARUCO_DICT_NAME_TO_ID = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
}


class ArucoLocalizer:
    def __init__(self, dict_name: str = "DICT_4X4_50", corner_ids: list[int] | None = None):
        self.corner_ids = corner_ids or [0, 1, 2, 3]
        dictionary_id = ARUCO_DICT_NAME_TO_ID.get(dict_name, cv2.aruco.DICT_4X4_50)
        self.dictionary = cv2.aruco.getPredefinedDictionary(dictionary_id)
        self.params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.dictionary, self.params)

    def detect_map_homography(self, frame: np.ndarray, map_size: tuple[int, int]) -> tuple[np.ndarray | None, int]:
        corners, ids, _ = self.detector.detectMarkers(frame)
        if ids is None:
            return None, 0
        id_to_corner = {}
        for marker_corners, marker_id_arr in zip(corners, ids):
            marker_id = int(marker_id_arr[0])
            if marker_id not in self.corner_ids:
                continue
            pts = marker_corners[0]
            center = np.mean(pts, axis=0)
            id_to_corner[marker_id] = center
        if len(id_to_corner) < 4:
            return None, len(id_to_corner)

        src = np.array([id_to_corner[mid] for mid in self.corner_ids], dtype=np.float32)
        w, h = map_size
        dst = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32)
        homography = cv2.getPerspectiveTransform(src, dst)
        return homography, 4
