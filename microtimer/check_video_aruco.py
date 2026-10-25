import cv2
import sys
import numpy as np

def check_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open {video_path}")
        return

    # Check a few frames to see if they find markers. Sometimes the first frame is black.
    found_any = False
    unique_ids = set()
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        corners, ids, rejected = detector.detectMarkers(frame)
        if ids is not None and len(ids) > 0:
            for i in ids.flatten():
                unique_ids.add(i)
            found_any = True
            
        frame_count += 1
        if frame_count % 30 == 0:
            pass # just to keep it running

    if not found_any:
        print("No markers found in any frame.")
    else:
        print(f"Checked {frame_count} frames. Unique markers found: {sorted(list(unique_ids))}")

    if not found_any:
        print("No markers found in any frame.")

    print("Done checking.")

if __name__ == "__main__":
    check_video("d:/SRC/micromouse_timer/mock_run_real.mp4")
