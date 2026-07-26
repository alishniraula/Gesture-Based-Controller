import cv2
import pyautogui
import numpy as np
import time

# --- MEDIAPIPE TASKS & VISION IMPORT ---
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# System Optimization & Safety Settings
pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = False
screen_w, screen_h = pyautogui.size()

# Initialize Hand Landmarker Model
import urllib.request
import os
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("Downloading hand tracking model...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)
    print("Model downloaded successfully!")

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    running_mode=vision.RunningMode.VIDEO
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

# Tracking & Smoothing Variables
prev_x, prev_y = 0, 0
smooth_factor = 3
last_action_time = 0
mode_switch_time = 0

# Double Pinch Tracker for Right Click
last_pinch_time = 0

# Alt+Tab Holding Tracker
alt_tab_active = False
last_tab_cycle_time = 0

# Swipe Tracking Variables
prev_palm_x = 0
swipe_cooldown_until = 0

# Game Mode Single-Tap Latch
last_game_gesture = None

modes = ["DESKTOP", "PRESENTATION", "GAME"]
current_mode_idx = 0
current_mode = modes[current_mode_idx]

HAND_CONNECTIONS = [
    (0,1), (1,2), (2,3), (3,4),
    (0,5), (5,6), (6,7), (7,8),
    (5,9), (9,10), (10,11), (11,12),
    (9,13), (13,14), (14,15), (15,16),
    (13,17), (17,18), (18,19), (19,20), (0,17)
]

print(f"System Initialized. Active Mode: {current_mode}")
frame_timestamp_ms = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    frame_timestamp_ms += 33
    
    detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)
    current_time = time.time()
    active_gesture_text = "Neutral / Waiting for Action"

    if detection_result.hand_landmarks:
        hand_landmarks = detection_result.hand_landmarks[0]
        
        # Draw Skeleton
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
        for p1, p2 in HAND_CONNECTIONS:
            cv2.line(frame, pts[p1], pts[p2], (0, 255, 0), 2)
        for pt in pts:
            cv2.circle(frame, pt, 4, (0, 0, 255), -1)

        # Key Landmarks
        index_tip = hand_landmarks[8]
        thumb_tip = hand_landmarks[4]
        middle_tip = hand_landmarks[12]
        ring_tip = hand_landmarks[16]
        pinky_tip = hand_landmarks[20]
        wrist = hand_landmarks[0]
        
        palm_x = hand_landmarks[9].x * w
        palm_y = hand_landmarks[9].y * h

        # Strict Finger Extension Check
        index_open = index_tip.y < hand_landmarks[6].y
        middle_open = middle_tip.y < hand_landmarks[10].y
        ring_open = ring_tip.y < hand_landmarks[14].y
        pinky_open = pinky_tip.y < hand_landmarks[18].y

        # Thumb Tucked Check
        thumb_tucked = abs(thumb_tip.x - hand_landmarks[17].x) < 0.12

        # Scale Factor based on hand size
        hand_scale = np.hypot((hand_landmarks[9].x - wrist.x)*w, (hand_landmarks[9].y - wrist.y)*h)
        if hand_scale == 0: hand_scale = 1.0

        # Pinch Threshold for Desktop Click
        idx_thumb_dist = np.hypot((index_tip.x - thumb_tip.x)*w, (index_tip.y - thumb_tip.y)*h) / hand_scale
        is_pinching_idx = idx_thumb_dist < 0.14

        # Palm Velocity
        if prev_palm_x == 0:
            prev_palm_x = palm_x
        palm_velocity = palm_x - prev_palm_x
        prev_palm_x = palm_x

        # Hand-Entry Shield (Ignore gestures in bottom 20% of frame)
        is_hand_entering = palm_y > (h * 0.80)

        # --- MODE SWITCHING (PINKY UP ONLY FOR 1 SEC) ---
        if pinky_open and not index_open and not middle_open and not ring_open:
            if mode_switch_time == 0:
                mode_switch_time = current_time
            elif current_time - mode_switch_time > 1.0:
                current_mode_idx = (current_mode_idx + 1) % len(modes)
                current_mode = modes[current_mode_idx]
                mode_switch_time = 0
                last_game_gesture = None
                if alt_tab_active:
                    pyautogui.keyUp('alt')
                    alt_tab_active = False
                time.sleep(0.4)
        else:
            mode_switch_time = 0

        can_act = (current_time - last_action_time > 0.3)

        # ==========================================
        # 1. DESKTOP MODE
        # ==========================================
        if current_mode == "DESKTOP":
            four_or_five_open = index_open and middle_open and ring_open

            # MULTI-TAB APP SWITCHER (ALT + TAB)
            if four_or_five_open and not is_pinching_idx and not is_hand_entering:
                if not alt_tab_active:
                    pyautogui.keyDown('alt')
                    pyautogui.press('tab')
                    alt_tab_active = True
                    last_tab_cycle_time = current_time
                    active_gesture_text = "ALT+TAB ACTIVE (HOLDING)"
                else:
                    if current_time - last_tab_cycle_time > 0.5:
                        pyautogui.press('tab')
                        last_tab_cycle_time = current_time
                    active_gesture_text = "CYCLING NEXT APP..."

            else:
                if alt_tab_active:
                    pyautogui.keyUp('alt')
                    alt_tab_active = False
                    active_gesture_text = "SELECTED SOFTWARE"
                    last_action_time = current_time

                # LEFT & RIGHT CLICK
                elif is_pinching_idx and can_act and not is_hand_entering:
                    if current_time - last_pinch_time < 0.35:
                        pyautogui.rightClick()
                        active_gesture_text = "*** RIGHT CLICK (DOUBLE PINCH) ***"
                        cv2.circle(frame, pts[8], 18, (255, 0, 0), -1)
                        last_pinch_time = 0
                        last_action_time = current_time
                    else:
                        pyautogui.click()
                        active_gesture_text = "*** LEFT CLICK ***"
                        cv2.circle(frame, pts[8], 15, (0, 255, 0), -1)
                        last_pinch_time = current_time
                        last_action_time = current_time

                # MOVE CURSOR
                elif index_open and not middle_open and not ring_open and not pinky_open and not is_pinching_idx and not is_hand_entering:
                    target_x = int(np.interp(index_tip.x * w, (100, w - 100), (0, screen_w)))
                    target_y = int(np.interp(index_tip.y * h, (100, h - 100), (0, screen_h)))
                    curr_x = prev_x + (target_x - prev_x) / smooth_factor
                    curr_y = prev_y + (target_y - prev_y) / smooth_factor
                    prev_x, prev_y = curr_x, curr_y
                    
                    pyautogui.moveTo(curr_x, curr_y)
                    active_gesture_text = "Moving Cursor"

                # SCROLL UP
                elif index_open and middle_open and not ring_open and not pinky_open and not is_hand_entering:
                    pyautogui.scroll(80)
                    active_gesture_text = "Scrolling Up"

                # PRESS ENTER
                elif index_open and middle_open and ring_open and not pinky_open and can_act and not is_hand_entering:
                    pyautogui.press('enter')
                    active_gesture_text = "PRESS ENTER"
                    last_action_time = current_time

                # SWITCH TAB (CTRL + TAB)
                elif not index_open and middle_open and ring_open and pinky_open and can_act and not is_hand_entering:
                    pyautogui.hotkey('ctrl', 'tab')
                    active_gesture_text = "NEXT TAB (CTRL+TAB)"
                    last_action_time = current_time

                # SCROLL DOWN
                elif (not index_open and not middle_open and not ring_open and not pinky_open 
                      and thumb_tucked and not is_pinching_idx and not is_hand_entering):
                    pyautogui.scroll(-80)
                    active_gesture_text = "Scrolling Down"

        # ==========================================
        # 2. PRESENTATION MODE
        # ==========================================
        elif current_mode == "PRESENTATION":
            if current_time < swipe_cooldown_until:
                active_gesture_text = "[SWIPE COOLING DOWN - RESET HAND]"
            else:
                if palm_velocity > 35 and not is_hand_entering:
                    pyautogui.press('right')
                    active_gesture_text = ">>> SWIPE RIGHT (NEXT SLIDE)"
                    swipe_cooldown_until = current_time + 0.7
                    last_action_time = current_time

                elif palm_velocity < -35 and not is_hand_entering:
                    pyautogui.press('left')
                    active_gesture_text = "<<< SWIPE LEFT (PREV SLIDE)"
                    swipe_cooldown_until = current_time + 0.7
                    last_action_time = current_time

                elif index_open and middle_open and not ring_open and can_act and not is_hand_entering:
                    pyautogui.press('f5')
                    active_gesture_text = "Start Slideshow (F5)"
                    last_action_time = current_time

                elif not index_open and not middle_open and not ring_open and can_act and not is_hand_entering:
                    pyautogui.press('escape')
                    active_gesture_text = "Exit Slideshow (Esc)"
                    last_action_time = current_time

        # ==========================================
        # 3. GAME MODE (INDEX UP = MOVE RIGHT)
        # ==========================================
        elif current_mode == "GAME":
            current_detected_gesture = None
            
            if not is_hand_entering:
                # 1. MOVE RIGHT: Index Finger UP Only
                if index_open and not middle_open and not ring_open and not pinky_open:
                    current_detected_gesture = "RIGHT"

                # 2. MOVE LEFT: Peace Sign (Index & Middle UP)
                elif index_open and middle_open and not ring_open and not pinky_open:
                    current_detected_gesture = "LEFT"

                # 3. JUMP: All 4 Fingers Extended UP
                elif index_open and middle_open and ring_open and pinky_open:
                    current_detected_gesture = "JUMP"

                # 4. SLIDE / DUCK: Closed Fist
                elif not index_open and not middle_open and not ring_open and not pinky_open:
                    current_detected_gesture = "DUCK"

            # Execute command ONLY on initial gesture change
            if current_detected_gesture != last_game_gesture:
                if current_detected_gesture == "RIGHT":
                    pyautogui.press('right')
                    active_gesture_text = ">>> MOVE RIGHT"
                elif current_detected_gesture == "LEFT":
                    pyautogui.press('left')
                    active_gesture_text = "<<< MOVE LEFT"
                elif current_detected_gesture == "JUMP":
                    pyautogui.press('up')
                    active_gesture_text = "^^^ JUMP"
                elif current_detected_gesture == "DUCK":
                    pyautogui.press('down')
                    active_gesture_text = "vvv SLIDE / DUCK"
                
                last_game_gesture = current_detected_gesture

            elif current_detected_gesture is not None:
                active_gesture_text = f"Holding [{current_detected_gesture}] - Action Sent"
            else:
                active_gesture_text = "Neutral Position (Idle)"

    # On-Screen HUD Overlay
    cv2.rectangle(frame, (10, 10), (480, 110), (0, 0, 0), -1)
    cv2.putText(frame, f"MODE: {current_mode}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(frame, f"ACTION: {active_gesture_text}", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    if mode_switch_time > 0:
        cv2.putText(frame, "HOLD PINKY TO SWITCH MODE...", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    cv2.imshow("Master Gesture Control System", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if alt_tab_active:
    pyautogui.keyUp('alt')

cap.release()
cv2.destroyAllWindows()