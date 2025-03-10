import cv2
import torch
from ultralytics import YOLO
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from pynput import keyboard

model = YOLO("model/model.pt")
class_names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
class_colors = {
    "A": (0, 0, 255),  # Red
    "B": (0, 255, 0),  # Green
    "C": (255, 0, 0),  # Blue
    "D": (255, 255, 0),  # Yellow
    "E": (0, 255, 255),  # Cyan
    "F": (255, 0, 255),  # Magenta
    "G": (128, 0, 0),  # Dark Red
    "H": (0, 128, 0),  # Dark Green
    "I": (0, 0, 128),  # Dark Blue
    "J": (128, 128, 0),  # Olive
    "K": (0, 128, 128),  # Teal
    "L": (128, 0, 128),  # Purple
    "M": (192, 192, 192),  # Silver
    "N": (255, 165, 0),  # Orange
    "O": (255, 69, 0),  # Red-Orange
    "P": (255, 105, 180),  # Hot Pink
    "Q": (255, 228, 181),  # Moccasin
    "R": (139, 0, 0),  # Dark Red
    "S": (0, 139, 139),  # Dark Cyan
    "T": (139, 69, 19),  # Saddle Brown
    "U": (255, 215, 0),  # Gold
    "V": (138, 43, 226),  # Blue Violet
    "W": (255, 255, 255),  # White
    "X": (169, 169, 169),  # Dark Gray
    "Y": (255, 255, 224),  # Light Yellow
    "Z": (70, 130, 180)   # Steel Blue
}

camera = cv2.VideoCapture(0)
root = Tk()
root.title("Live ASL Recognition")



style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=10, relief="flat")
style.configure("TLabel", font=("Helvetica", 14))

control_frame = Frame(root, bg="#3498db", padx=20, pady=20)
control_frame.pack(fill=BOTH, expand=True)

image_label = Label(root)
image_label.pack(fill=BOTH, expand=True)

stop_live_feed = False
sentence = ""
current_word = ""

def show_live_feed():
    global stop_live_feed, sentence, current_word
    ret, frame = camera.read()
    if not ret:
        print("Failed to grab frame")
        return

    results = model(frame, conf=0.25)

    for box, cls in zip(results[0].boxes.xyxy, results[0].boxes.cls):
        x1, y1, x2, y2 = box.tolist()
        cls = int(cls)
        label = class_names[cls]
        color = class_colors.get(label, (255, 255, 255))

        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        label_width, label_height = label_size

        text_x = int(x1) + 5
        text_y = int(y1) + label_height + 5
        text_y = min(int(y2) - 5, text_y)

        cv2.rectangle(frame, (text_x - 5, text_y - label_height - 5), (text_x + label_width + 5, text_y + 5), color, -1)
        cv2.putText(frame, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        current_word = label

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img_tk = ImageTk.PhotoImage(image=img)

    image_label.img_tk = img_tk
    image_label.configure(image=img_tk)

    if stop_live_feed:
        return

    root.after(10, show_live_feed)

def update_sentence_display():
    sentence_label.config(text=sentence)

def stop_feed():
    global stop_live_feed
    stop_live_feed = True
    camera.release()
    image_label.configure(image=None)
    image_label.img_tk = None

def start_live_feed():
    global stop_live_feed
    stop_live_feed = False
    image_label.configure(image=None)
    if not camera.isOpened():
        camera.open(0)
    show_live_feed()
    for widget in control_frame.winfo_children():
        widget.pack_forget()
    stop_button = Button(control_frame, text="Stop Live Detection", command=stop_feed, bg="#e74c3c", fg="white", font=("Helvetica", 14), width=20)
    stop_button.pack(pady=20)

def on_press(key):
    global sentence, current_word
    try:
        if key == keyboard.Key.enter:
            sentence += current_word + " "
            current_word = ""
        elif key == keyboard.Key.space or key == keyboard.Key.tab:
            sentence += " "
            current_word = ""
        elif key == keyboard.Key.backspace:
            words = sentence.split()
            if words:
                sentence = " ".join(words[:-1]) + " "
                current_word = ""
            else:
                current_word = current_word[:-1]
        update_sentence_display()
    except AttributeError:
        pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

sentence_label = Label(root, text=sentence, font=("Helvetica", 20), width=30, height=2)
sentence_label.pack(pady=10)

root.after(100, start_live_feed)
root.mainloop()
