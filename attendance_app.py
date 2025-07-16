import cv2
import face_recognition
import numpy as np
import os
import csv
import time
from datetime import datetime

# --- Configuration and Setup ---
STUDENT_IMAGES_DIR = 'Student_Images'
STUDENT_DATA_FILE = 'student_data.csv'
CHECKMARK_ICON_FILE = 'checkmark.png'
ATTENDANCE_LOG_FILE = 'attendance_log.csv'
RESIZE_FACTOR = 4
SUCCESS_COOLDOWN = 5

# --- METHOD 1: Stricter Tolerance ---
# A lower number is stricter. 0.45 is a good starting point.
MATCH_TOLERANCE = 0.45

# --- Helper Functions ---

def load_student_data():
    """
    METHOD 2 IMPLEMENTATION:
    Loads student data from CSV and encodes MULTIPLE images per student.
    It finds all image files in STUDENT_IMAGES_DIR that start with the
    base filename from the CSV (e.g., 'Muhammad_Bilal').
    """
    known_face_encodings = []
    known_face_names = []
    student_data_map = {} # Maps a student name to their full data row

    print("Loading student data and encoding faces...")
    try:
        with open(STUDENT_DATA_FILE, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                student_name = row['Name']
                base_filename = os.path.splitext(row['ImageFile'])[0]
                student_data_map[student_name] = row
                
                images_found = 0
                for filename in os.listdir(STUDENT_IMAGES_DIR):
                    if filename.startswith(base_filename):
                        image_path = os.path.join(STUDENT_IMAGES_DIR, filename)
                        try:
                            student_image = face_recognition.load_image_file(image_path)
                            encodings = face_recognition.face_encodings(student_image)
                            if encodings:
                                known_face_encodings.append(encodings[0])
                                known_face_names.append(student_name) # Link encoding to a name
                                images_found += 1
                            else:
                                print(f"Warning: No face found in {filename}. Skipping.")
                        except Exception as e:
                            print(f"Error processing {filename}: {e}")
                
                if images_found == 0:
                    print(f"Warning: No image files found for {student_name} starting with '{base_filename}'")

    except FileNotFoundError:
        print(f"Error: The file {STUDENT_DATA_FILE} was not found.")
        return [], [], {}
        
    print(f"...Loading complete. {len(known_face_encodings)} total images encoded.")
    return known_face_encodings, known_face_names, student_data_map

# (mark_attendance, overlay_transparent, draw_profile, draw_default_ui are unchanged)
def mark_attendance(student_id, student_name):
    today_str = datetime.now().strftime('%Y-%m-%d'); now_str = datetime.now().strftime('%H:%M:%S')
    try:
        with open(ATTENDANCE_LOG_FILE, 'r', newline='') as f:
            for row in csv.reader(f):
                if len(row) == 4 and row[0] == student_id and row[2] == today_str:
                    return
    except FileNotFoundError: pass
    with open(ATTENDANCE_LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0: writer.writerow(['ID', 'Name', 'Date', 'Time'])
        writer.writerow([student_id, student_name, today_str, now_str])
        print(f"Attendance marked for {student_name} at {now_str}")

def overlay_transparent(background, overlay, x, y):
    bg_h, bg_w, _ = background.shape; h, w, _ = overlay.shape; overlay_image = overlay[:, :, :3]; mask = overlay[:, :, 3:] / 255.0
    if x >= bg_w or y >= bg_h: return background
    h, w = min(h, bg_h - y), min(w, bg_w - x); roi = background[y:y+h, x:x+w]
    background[y:y+h, x:x+w] = (1.0 - mask[:h, :w]) * roi + mask[:h, :w] * overlay_image[:h, :w]
    return background

def draw_profile(canvas, student_info, profile_pic):
    canvas_w = canvas.shape[1]; card_x, card_y, card_w, card_h = canvas_w - 320, 80, 300, 380
    cv2.rectangle(canvas, (card_x, card_y), (card_x + card_w, card_y + card_h), (255, 255, 255), cv2.FILLED)
    cv2.rectangle(canvas, (card_x, card_y), (card_x + card_w, card_y + card_h), (128, 80, 224), 3)
    if profile_pic is not None:
        profile_pic_resized = cv2.resize(profile_pic, (150, 150)); pic_y, pic_x = card_y + 20, card_x + (card_w - 150) // 2
        canvas[pic_y : pic_y + 150, pic_x : pic_x + 150] = profile_pic_resized
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(canvas, student_info['Name'], (card_x + 20, card_y + 210), font, 0.8, (0, 0, 0), 1)
    cv2.rectangle(canvas, (card_x + 20, card_y + 240), (card_x + card_w - 20, card_y + 270), (128, 80, 224), cv2.FILLED)
    cv2.putText(canvas, f"ID: {student_info['ID']}", (card_x + 30, card_y + 262), font, 0.6, (255, 255, 255), 1)
    cv2.rectangle(canvas, (card_x + 20, card_y + 280), (card_x + card_w - 20, card_y + 310), (128, 80, 224), cv2.FILLED)
    cv2.putText(canvas, f"Major: {student_info['Major']}", (card_x + 30, card_y + 302), font, 0.6, (255, 255, 255), 1)

def draw_default_ui(canvas):
    canvas_w = canvas.shape[1]; card_x, card_y, card_w, card_h = canvas_w - 320, 80, 300, 380
    cv2.rectangle(canvas, (card_x, card_y), (card_x + card_w, card_y + card_h), (255, 255, 255), cv2.FILLED)
    cv2.rectangle(canvas, (card_x, card_y), (card_x + card_w, card_y + card_h), (128, 80, 224), 3)
    cv2.putText(canvas, "Scan Your Face", (card_x + 40, card_y + 200), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 1)

def main():
    known_face_encodings, known_face_names, student_data_map = load_student_data()
    if not known_face_encodings: return

    video_capture = cv2.VideoCapture(0)
    cam_w = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)); cam_h = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    canvas_w, canvas_h = cam_w + 340, cam_h + 60
    
    try:
        checkmark_icon = cv2.imread(CHECKMARK_ICON_FILE, cv2.IMREAD_UNCHANGED)
        checkmark_icon = cv2.resize(checkmark_icon, (128, 128))
    except Exception: checkmark_icon = None

    app_state = "SCANNING"; success_timestamp = 0
    last_known_data = None; process_this_frame = True; face_locations = []

    while True:
        ret, frame = video_capture.read()
        if not ret: break

        ui_canvas = np.full((canvas_h, canvas_w, 3), (240, 235, 216), np.uint8)
        cv2.rectangle(ui_canvas, (0, 0), (canvas_w, 60), (128, 80, 224), cv2.FILLED)
        cv2.putText(ui_canvas, "ATTENDANCE SYSTEM", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ui_canvas[60:60+cam_h, 20:20+cam_w] = frame

        if app_state == "SCANNING":
            if process_this_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=1.0/RESIZE_FACTOR, fy=1.0/RESIZE_FACTOR)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                if face_encodings:
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encodings[0])
                    if len(face_distances) > 0:
                        best_match_index = np.argmin(face_distances)
                        # ---- THE CRITICAL ACCURACY CHECK ----
                        if face_distances[best_match_index] < 0.5:  # Using the stricter tolerance
                            name = known_face_names[best_match_index]
                            last_known_data = student_data_map[name]
                            
                            app_state = "SUCCESS"
                            success_timestamp = time.time()
                            mark_attendance(last_known_data['ID'], last_known_data['Name'])
            
            process_this_frame = not process_this_frame
            if face_locations:
                top, right, bottom, left = face_locations[0]
                top *= RESIZE_FACTOR; right *= RESIZE_FACTOR; bottom *= RESIZE_FACTOR; left *= RESIZE_FACTOR
                cv2.rectangle(ui_canvas, (left + 20, top + 60), (right + 20, bottom + 60), (0, 255, 0), 3)
            draw_default_ui(ui_canvas)

        elif app_state == "SUCCESS":
            # (This success state logic remains unchanged)
            overlay = ui_canvas[60:60+cam_h, 20:20+cam_w].copy()
            cv2.rectangle(overlay, (0, 0), (cam_w, cam_h), (0, 180, 0), -1)
            cv2.addWeighted(overlay, 0.7, ui_canvas[60:60+cam_h, 20:20+cam_w], 0.3, 0, ui_canvas[60:60+cam_h, 20:20+cam_w])
            if checkmark_icon is not None:
                icon_x = 20 + (cam_w - 128) // 2; icon_y = 60 + (cam_h - 128) // 2 - 30
                overlay_transparent(ui_canvas, checkmark_icon, icon_x, icon_y)
            cv2.putText(ui_canvas, "Attendance Marked", (20 + cam_w // 2 - 180, 60 + cam_h // 2 + 80), cv2.FONT_HERSHEY_TRIPLEX, 1.5, (255, 255, 255), 2)
            if last_known_data:
                profile_pic_path = os.path.join(STUDENT_IMAGES_DIR, last_known_data['ImageFile'])
                profile_pic = cv2.imread(profile_pic_path)
                draw_profile(ui_canvas, last_known_data, profile_pic)
            if time.time() - success_timestamp > SUCCESS_COOLDOWN:
                app_state = "SCANNING"; last_known_data = None; face_locations = []
        
        cv2.imshow('Attendance System', ui_canvas)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()