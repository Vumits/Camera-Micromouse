import cv2
import os

def generate_markers():
    output_dir = "aruco_markers"
    os.makedirs(output_dir, exist_ok=True)
    
    # Timer default uses DICT_4X4_50
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker_size = 400  # High resolution for clear printing
    
    # The default config tracks markers 0, 1, 2, 3
    for m_id in [0, 1, 2, 3]:
        if hasattr(cv2.aruco, "generateImageMarker"):
            img = cv2.aruco.generateImageMarker(dictionary, m_id, marker_size)
        else:
            img = cv2.aruco.drawMarker(dictionary, m_id, marker_size)
            
        # Add a white border so the marker is easily cut/visible against black backgrounds
        bordered_img = cv2.copyMakeBorder(
            img, 50, 50, 50, 50, 
            cv2.BORDER_CONSTANT, value=[255, 255, 255]
        )
            
        filename = os.path.join(output_dir, f"marker_{m_id}.png")
        cv2.imwrite(filename, bordered_img)
        print(f"[{m_id}] Generated: {filename}")
        
    print(f"\nSuccessfully generated 4 markers in the '{output_dir}' directory.")
    print("Please print these images and place them at the 4 corners of your physical map.")

if __name__ == "__main__":
    generate_markers()
