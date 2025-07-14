
import pyautogui
import threading
import time
from collections import deque
from detect_gesture import process_frame, get_index_finger_position

# --- BUFFER TRUNG BÌNH / EMA ---
buffer_size = 7
pos_x_buffer = deque(maxlen=buffer_size)
pos_y_buffer = deque(maxlen=buffer_size)

# --- CẤU HÌNH LỌC MƯỢT ---
filter_mode = "ema"
ema_alpha = 0.2
ema_x = None
ema_y = None

# --- GLOBAL CONFIGURATION ---
global_click_lock = threading.Lock()
global_click_frame = None

prev_pixel_x = None
prev_pixel_y = None
smoothed_x, smoothed_y = pyautogui.position()

speed = 7.0
sensitivity = 1
click_cooldown = 0.5
last_click_time = 0
delta_threshold = 2
target_fps = 30

def click_processing():
    global global_click_frame, prev_pixel_x, prev_pixel_y, last_click_time
    global smoothed_x, smoothed_y, ema_x, ema_y

    last_frame_time = time.time()
    mouse_locked = False

    while True:
        now = time.time()
        dt = now - last_frame_time
        if dt < 1 / target_fps:
            time.sleep(1 / target_fps - dt)
        last_frame_time = time.time()

        frame_to_process = None
        with global_click_lock:
            if global_click_frame is not None:
                frame_to_process = global_click_frame.copy()
        if frame_to_process is None:
            continue

        gestures_result, handedness_result, hand_landmarks_result = process_frame(frame_to_process)
        if not hand_landmarks_result:
            prev_pixel_x, prev_pixel_y = None, None
            continue

        height, width, _ = frame_to_process.shape
        screen_width, screen_height = pyautogui.size()
        right_hand_found = False

        mouse_locked = any(
            handedness_result[i][0].category_name == "Left" and
            gestures_result[i][0].category_name.lower() == "victory"
            for i in range(len(hand_landmarks_result))
            if gestures_result[i]
        )

        for i in range(len(hand_landmarks_result)):
            handed_label = handedness_result[i][0].category_name
            gesture = gestures_result[i][0].category_name.lower() if gestures_result[i] else None

            if handed_label == "Left" and gesture:
                if gesture == "open_palm":
                    center_x = screen_width // 2
                    center_y = screen_height // 2
                    pyautogui.moveTo(center_x, center_y)
                    prev_pixel_x, prev_pixel_y = None, None
                    smoothed_x, smoothed_y = center_x, center_y
                    pos_x_buffer.clear()
                    pos_y_buffer.clear()
                    ema_x, ema_y = center_x, center_y
                elif gesture == "closed_fist":
                    current_time = time.time()
                    if current_time - last_click_time > click_cooldown:
                        pyautogui.click()
                        last_click_time = current_time
                elif gesture == "thumb_up":
                    pyautogui.scroll(100)
                elif gesture == "thumb_down":
                    pyautogui.scroll(-100)

            if handed_label == "Right" and not mouse_locked:
                right_hand_found = True
                pixel_x, pixel_y = get_index_finger_position(hand_landmarks_result[i], frame_to_process.shape)
                if pixel_x is None or pixel_y is None:
                    continue

                if prev_pixel_x is None or prev_pixel_y is None:
                    prev_pixel_x, prev_pixel_y = pixel_x, pixel_y
                    curr_x, curr_y = pyautogui.position()
                    smoothed_x, smoothed_y = curr_x, curr_y
                    pos_x_buffer.clear()
                    pos_y_buffer.clear()
                    pos_x_buffer.append(curr_x)
                    pos_y_buffer.append(curr_y)
                    ema_x, ema_y = curr_x, curr_y
                else:
                    dx = (pixel_x - prev_pixel_x) * speed * sensitivity
                    dy = (pixel_y - prev_pixel_y) * speed * sensitivity
                    curr_x, curr_y = pyautogui.position()
                    new_x = max(0, min(curr_x + dx, screen_width))
                    new_y = max(0, min(curr_y + dy, screen_height))

                    if filter_mode == "mean":
                        pos_x_buffer.append(new_x)
                        pos_y_buffer.append(new_y)
                        smoothed_x = sum(pos_x_buffer) / len(pos_x_buffer)
                        smoothed_y = sum(pos_y_buffer) / len(pos_y_buffer)
                    elif filter_mode == "ema":
                        ema_x = ema_alpha * new_x + (1 - ema_alpha) * ema_x
                        ema_y = ema_alpha * new_y + (1 - ema_alpha) * ema_y
                        smoothed_x, smoothed_y = ema_x, ema_y
                    else:
                        smoothed_x, smoothed_y = new_x, new_y

                    if abs(curr_x - smoothed_x) > delta_threshold or abs(curr_y - smoothed_y) > delta_threshold:
                        pyautogui.moveTo(int(smoothed_x), int(smoothed_y))

                prev_pixel_x = pixel_x
                prev_pixel_y = pixel_y

        if not right_hand_found:
            prev_pixel_x, prev_pixel_y = None, None

def update_click_frame(frame):
    global global_click_frame
    with global_click_lock:
        global_click_frame = frame.copy()
