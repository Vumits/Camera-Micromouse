import cv2
import numpy as np
import os

def create_synthetic_run(output_path="mock_run.mp4", duration_sec=5, fps=30):
    w, h = 1000, 1000
    map_w, map_h = 800, 800
    ox, oy = 100, 100

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker_size = 80

    markers = [0, 1, 2, 3] # top-left, top-right, bottom-right, bottom-left
    marker_imgs = []
    for m_id in markers:
        # Compatibility across cv2 versions
        if hasattr(cv2.aruco, "generateImageMarker"):
            img = cv2.aruco.generateImageMarker(dictionary, m_id, marker_size)
        else:
            img = cv2.aruco.drawMarker(dictionary, m_id, marker_size)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        marker_imgs.append(img)

    corners = [
        (ox, oy), 
        (ox + map_w - marker_size, oy), 
        (ox + map_w - marker_size, oy + map_h - marker_size),
        (ox, oy + map_h - marker_size)
    ]

    base_frame = np.ones((h, w, 3), dtype=np.uint8) * 200
    cv2.rectangle(base_frame, (ox, oy), (ox+map_w, oy+map_h), (50, 50, 50), -1)

    for corner, m_img in zip(corners, marker_imgs):
        cx, cy = corner
        base_frame[cy:cy+marker_size, cx:cx+marker_size] = m_img

    total_frames = duration_sec * fps
    
    for i in range(total_frames):
        frame = base_frame.copy()
        
        # Mouse stays still initially, then moves rapidly, then stays at goal
        # T=0 to T=1 (0 to 30): Still at ox+12, oy+100
        # T=1 to T=3.5: Moving to center
        # T=3.5 to T=5: Still at center
        
        t = i / fps
        mx, my = ox + 15, oy + 80
        
        if t > 1.0 and t < 3.5:
            progress = (t - 1.0) / 2.5
            mx = int((ox + 15) + progress * (map_w/2 - 15))
            my = int((oy + 80) + progress * (map_h/2 - 80))
        elif t >= 3.5:
            mx = ox + map_w//2
            my = oy + map_h//2
            
        cv2.rectangle(frame, (mx-15, my-15), (mx+15, my+15), (0, 0, 255), -1)
        
        # Add faint noise
        noise = np.random.randint(0, 10, (h, w, 3), dtype=np.uint8)
        frame = cv2.add(frame, noise)

        out.write(frame)

    out.release()
    print(f"Synthetic video saved at: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    create_synthetic_run()
