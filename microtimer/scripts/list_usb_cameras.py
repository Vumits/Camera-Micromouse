from __future__ import annotations

import argparse

import cv2


def probe_index(index: int, backend: int) -> tuple[bool, tuple[int, int] | None]:
    cap = cv2.VideoCapture(index, backend)
    if not cap.isOpened():
        cap.release()
        return False, None
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        return False, None
    h, w = frame.shape[:2]
    return True, (w, h)


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe USB camera indexes")
    parser.add_argument("--max-index", type=int, default=10)
    args = parser.parse_args()

    print("Scanning camera indexes...")
    found = 0
    for idx in range(args.max_index + 1):
        ok, size = probe_index(idx, cv2.CAP_DSHOW)
        backend_name = "CAP_DSHOW"
        if not ok:
            ok, size = probe_index(idx, cv2.CAP_MSMF)
            backend_name = "CAP_MSMF"
        if ok and size is not None:
            found += 1
            print(f"index={idx} backend={backend_name} frame={size[0]}x{size[1]}")
    if found == 0:
        print("No camera detected in scanned range.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
