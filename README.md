# Hand‑Gesture Mouse Control Demo

This demo lets you **control the mouse cursor with real‑time hand gestures** captured from your webcam. It is powered by MediaPipe for hand tracking, OpenCV for video I/O, and PyAutoGUI / AutoPy for cursor actions.

---

## Features

| Feature | Description |
|---------|-------------|
| Hand‑gesture recognition | Detects one or more hands and classifies gestures (open palm, fist, etc.) |
| Mouse control | Moves cursor, left/right‑clicks, scrolling based on detected gestures |
| Stable FPS | Maintains ~30 FPS on a 640 × 480 webcam feed |
| Multi‑threaded | A separate thread handles mouse clicks for smoother interaction |

---

## System Requirements

* **Python ≥ 3.8**
* A webcam (720 p recommended)
* Windows / Linux / macOS  
  (tested on Windows 10 and Ubuntu 22.04)

---

## Quick Setup

```bash
# 1) Clone the repo
git clone https://github.com/honggquan24/hand-gesture-mouse-control.git
cd hand-gesture-mouse-control

# 2) Create & activate a Conda environment (Python ≥ 3.8)
conda create -n gesturemouse python=3.10
conda activate gesturemouse

# 3) Install dependencies with pip inside the Conda env
python -m pip install --upgrade pip
pip install -r requirements.txt
