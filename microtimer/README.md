# Micromouse Timer

Realtime micromouse timer designed for competition scoring using OpenCV and PyQt6 with a map-only tracking pipeline.

**Core Capabilities:**
- **Flexible Camera Input:** USB Cameras or IP Camera streams.
- **Auto-Localization:** 4-corner ArUco map localization with perspective warp to a standardized top-down 2D map.
- **Robust Motion Detection:** Uses `BackgroundSubtractorMOG2` for unaffected detection against shadow and lighting shifts at both Start Line and Goal Area.
- **Competition Features:** Finite-state-machine timer, Excel Reports, Auto-Save protection, and Audio Feedbacks (Beeps).

---

## 🛠️ Installation & Setup (Conda / Recommended)

This project relies on `pyqt6` and `opencv` which can encounter DLL/Library issues on Windows if not properly isolated. Conda is highly recommended.

### 1. Create Environment
Open Anaconda Prompt (or your terminal) and run:
```bash
conda env create -f environment.yml
```

### 2. Activate It
```bash
conda activate micromouse-timer
```
*(Tip for Updates: If you pull new code later, update using `conda env update -f environment.yml --prune`)*

---

## 🚀 How to Run the Timer

Once activated, start the application by running:
```bash
python -m app.main
```

### 1) Prepare Map & Camera
- Ensure the physical map has 4 ArUco markers placed at 4 corners. 
- You can generate high-resolution PNGs for printing by running:
  ```bash
  python scripts/generate_markers.py
  ```
  *(This will create a folder `aruco_markers/` containing printable `marker_0.png` through `marker_3.png` with correct borders)*
- Marker IDs must match `processing.corner_ids` inside `config/default.yaml` (default: 0, 1, 2, 3 from DICT_4X4_50).
- Keep camera fixed (top-down view is preferred) with sufficient ambient light.

### 2) Connect the Camera (UI sidebar)
- **Source:** select `usb` (for webcams) or `ip` (for RTSP/Streams or Local video files!).
- **Index/URL:** Enter the USB index (e.g. `0`, `1`) or the network URL.
- **Connect:** Click this to see the live feed. The image stretches dynamically to fill the screen layout for external monitors.

### 3) Start Official Session (Competition Mode)
1. Enter the **Team name** and set the session **Minutes** (countdown duration).
2. Click **Start Session**. This will:
   - Begin the global countdown.
   - Automatically generate a `.csv` auto-save backup in `exports/` folder to prevent data loss.
3. For each attempt, click **Next Run** (which resets tracking and Arms the timer).
4. **Audio Feedbacks:**
   - **Start:** When the mouse crosses the start line, the app emits a short beep (Timer: `RUNNING`).
   - **Finish:** When the mouse enters the goal area and stays long enough, the app emits 3 high-pitch beeps (Timer: `FINISHED`).
5. **Early End:** If a team finishes early before the timer ends, simply click **Stop Session**. The final Excel file will be exported instantly!

---

## 🎮 Virtual Simulation (Mock Run)

If you don't have a physical map or camera nearby and just want to test the entire workflow (detectors, Excel generation, sounds):

1. **Generate the Mock Video:**
   Open a terminal in the project root and run:
   ```bash
   python scripts/create_mock_video.py
   ```
   *(This creates a file named `mock_run.mp4` containing a synthetic map, 4 ArUco markers, and an animated red "mouse").*

2. **Run it in the Timer App:**
   - Launch the Timer App (`python -m app.main`).
   - In the Camera panel, set **Source** to `ip`.
   - In **Index/URL**, type exactly `mock_run.mp4`.
   - Click **Connect**. The Timer will treat the video file as an IP stream.
   - Click **Arm** or **Start Session**, and watch the UI detect the moving red dot, start the timer, beep, and log the elapsed time!

---

## 🎛️ Configuration

All detection thresholds and UI settings can be customized in `config/default.yaml`. 

Notable Settings:
- `start_corner`: Defines where the starting line is located on the map. Supported values are `top_left` (default), `top_right`, `bottom_left`, or `bottom_right`. The **Goal Area** is always anchored in the exact center of the map.
- `map_inset_pct`: (Default: `0.0`). Set this > 0 (e.g., `0.05` for 5%) if you place the ArUco markers *outside* the actual playing maze. This shrinks the Start and Goal ROIs inwards so they don't trigger on the empty padding floor.
- `diff_threshold`: Controls how sensitive the MOG2 background subtractor is to movement (15-40).
- `start_ratio_threshold` / `goal_ratio_threshold`: Percentage of the Start/Goal area that must contain motion to trigger.
- `finish_consecutive_frames`: How many frames the mouse must remain inside the goal area to be recognized as completed.

To find your correct USB Camera Index, you can also run:
```bash
python scripts/list_usb_cameras.py --max-index 10
```
