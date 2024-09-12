import tkinter as tk
import pyautogui
import keyboard
import cv2
import numpy as np
from PIL import ImageGrab
import time


class ScreenRegionSelector:
    def __init__(self, root):
        self.root = root
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.region = None
        self.canvas = tk.Canvas(root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Button-1>", self.on_press)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red"
        )

    def on_drag(self, event):
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        self.end_x = event.x
        self.end_y = event.y
        x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
        x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)
        self.region = (x1, y1, x2, y2)
        self.root.destroy()


def preprocess_image(image):
    # Convert image to grayscale and apply thresholding
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return thresh


def find_and_click_template(region, template_paths):
    try:
        img = ImageGrab.grab(bbox=region)
        img_np = np.array(img)

        # Preprocess the screen image
        img_processed = preprocess_image(img_np)

        for template_path in template_paths:
            # Load the template
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            template_np = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)

            # Preprocess the template
            template_processed = preprocess_image(template_np)

            # Perform template matching
            result = cv2.matchTemplate(
                img_processed, template_processed, cv2.TM_CCOEFF_NORMED
            )
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            threshold = 0.4  # Try lowering the threshold for better matching
            if max_val >= threshold:
                template_height, template_width = template_np.shape[:2]
                top_left = max_loc
                center_x = top_left[0] + template_width // 2
                center_y = top_left[1] + template_height // 2
                screen_x = region[0] + center_x
                screen_y = region[1] + center_y
                pyautogui.click(screen_x, screen_y)
                return True
    except Exception as e:
        print(f"Unexpected error: {e}")
    return False


def main():
    root = tk.Tk()
    app = ScreenRegionSelector(root)
    root.mainloop()

    if app.region:
        template_paths = [
            "1.png",
            "9.png",
        ]  # Update with your template images
        stop_hotkey = "esc"

        print("Script started. Press ESC to stop.")
        running = True
        while running:
            if keyboard.is_pressed(
                stop_hotkey
            ):  # Use keyboard library to detect key press
                running = False
                print("Script stopped.")
            else:
                found = find_and_click_template(app.region, template_paths)
                if not found:
                    print("Template not found. Retrying...")
                time.sleep(0.5)  # Adjust the sleep time as needed
    else:
        print("No region defined. Exiting...")


if __name__ == "__main__":
    main()
