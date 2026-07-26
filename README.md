# Game-controller
Here is a clean, comprehensive **`README.md`** file tailored specifically for your GitHub repository. It explains the project, setup instructions, gesture controls, and troubleshooting in a clear, professional layout.

---

# 🖐️ AI Motion & Gesture Controller

An all-in-one, vision-based Human-Computer Interface (HCI) built with **Python**, **OpenCV**, and **Google MediaPipe**.

This system transforms your laptop’s webcam into an intelligent controller that allows you to control your desktop, navigate presentations, and play PC/browser games—**completely hardware-free and touchless**.

---

## 🌟 Key Features

* **Zero Custom Hardware:** Works on any standard laptop or PC using just a built-in webcam.
* **Dynamic Mode Switching:** Easily cycle between profiles by holding your pinky finger up for 1 second.
* **Smooth Mouse Motion:** Implements exponential moving average (EMA) smoothing to eliminate cursor jitter.
* **Hand-Entry & Anti-Spam Protection:** Features single-tap latches and a lower-screen shield zone to prevent accidental gestures.
* **Interactive HUD:** Displays real-time gesture feedback and mode indicators directly on the camera feed.

---

## 🎮 Control Modes & Gestures

Hold your **Pinky Finger UP Alone** for 1.0 second to switch between the following modes:

```
DESKTOP MODE  ➔  PRESENTATION MODE  ➔  GAME MODE

```

### 1. 🖥️ Desktop / OS Control Mode

Manage mouse navigation, software windows, and browser tabs effortlessly.

| Action | Hand Gesture | System Shortcut |
| --- | --- | --- |
| **Move Cursor** | ☝️ Index Finger UP Only | Mouse Cursor Tracking |
| **Left Click** | 🤏 Index + Thumb Single Pinch | Left Mouse Click |
| **Right Click** | 🤏 Index + Thumb **Double Pinch** | Right Mouse Click |
| **Scroll Up** | ✌️ Peace Sign *(Index + Middle UP)* | Mouse Scroll Up |
| **Scroll Down** | ✊ Closed Fist *(Thumb Tucked)* | Mouse Scroll Down |
| **Press Enter** | 🤟 3 Fingers UP *(Index + Middle + Ring)* | `Enter` Key |
| **Switch Apps (Alt+Tab)** | 🖐️ 4 or 5 Open Fingers *(Hold to cycle)* | `Alt + Tab` Carousel |
| **Switch Browser Tab** | 🖖 3 Fingers UP *(Middle + Ring + Pinky)* | `Ctrl + Tab` |

---

### 2. 📊 Presentation Control Mode

Present slides cleanly without needing a physical clicker or touching your laptop.

| Action | Hand Gesture | System Shortcut |
| --- | --- | --- |
| **Next Slide** | 👉 Swipe Hand Right | `Right Arrow` |
| **Previous Slide** | 👈 Swipe Hand Left | `Left Arrow` |
| **Start Slideshow** | ✌️ Peace Sign *(Index + Middle UP)* | `F5` Key |
| **Exit Slideshow** | ✊ Closed Fist | `Escape` Key |

---

### 3. 🕹️ Game Control Mode

Designed for endless runner games like *Subway Surfers*, *Temple Run*, or *Crossy Road* (works natively on sites like Poki or CrazyGames).

| Action | Hand Gesture | Keyboard Input |
| --- | --- | --- |
| **Move Right** | ☝️ Index Finger UP Only | `Right Arrow` |
| **Move Left** | ✌️ Peace Sign *(Index + Middle UP)* | `Left Arrow` |
| **Jump** | 🖐️ 4 or 5 Open Fingers | `Up Arrow` |
| **Slide / Duck** | ✊ Closed Fist | `Down Arrow` |

---

## 🛠️ Installation & Setup

### Prerequisites

Make sure you have **Python 3.8 – 3.11** installed on your system.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/gesture-game-controller.git
cd gesture-game-controller

```

### 2. Install Required Dependencies

Install all required libraries using `pip`:

```bash
pip install opencv-python mediapipe pyautogui numpy

```

### 3. Run the Controller

```bash
python controller.py

```

> **Note:** On first launch, the script will automatically download the 10 MB MediaPipe `hand_landmarker.task` vision model file into your project folder.

---

## ⚡ Performance & Troubleshooting Tips

* **Windows Administrator Rights:** If clicks or keypresses are blocked in certain full-screen games or admin windows, open your Command Prompt as **Administrator** before running `python controller.py`.
* **Browser Game Focus:** Make sure to click once inside the browser game window so keyboard signals (`Arrow Keys`) are captured by the game.
* **Lighting:** Ensure your face and hands are reasonably lit. Avoid strong backlights directly behind your head.
* **Exit Program:** Click on the OpenCV camera video feed window and press **`q`** on your keyboard to safely stop execution.

---

## 📜 Dependencies & Technologies

* [OpenCV](https://opencv.org/) – Real-time computer vision and image rendering.
* [MediaPipe Tasks](https://ai.google.dev/edge/mediapipe/solutions/guide) – High-fidelity 3D hand landmark extraction.
* [PyAutoGUI](https://pyautogui.readthedocs.io/) – Cross-platform OS-level keyboard and mouse simulation.
* [NumPy](https://numpy.org/) – Fast matrix mathematics and vector distance calculations.
