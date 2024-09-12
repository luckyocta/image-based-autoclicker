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


def find_and_click_template(region, template_paths):
    try:
        img = ImageGrab.grab(bbox=region)
        img_np = np.array(img)
        img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

        for template_path in template_paths:
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            template_rgb = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
            template_height, template_width = template_rgb.shape[:2]

            result = cv2.matchTemplate(img_rgb, template_rgb, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            threshold = 0.58  # Adjust the threshold as needed
            if max_val >= threshold:
                center_x = max_loc[0] + template_width // 2
                center_y = max_loc[1] + template_height // 2
                screen_x = region[0] + center_x
                screen_y = region[1] + center_y
                pyautogui.click(screen_x, screen_y)
                return True
            else:
                print(f"Template {template_path} not found. Max value: {max_val:.2f}")

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
        start_time = time.time()
        running = True
        while running:
            if keyboard.is_pressed(stop_hotkey):
                running = False
                print("Script stopped.")
            else:
                found = find_and_click_template(app.region, template_paths)
                if not found:
                    print("Template not found. Retrying...")
                # Reduce sleep time to increase responsiveness
                time.sleep(0.1)  # Adjust the sleep time as needed
                # Add a quick check to limit unnecessary processing
                if time.time() - start_time > 60:  # Run for up to 60 seconds
                    running = False
                    print("Time limit reached. Stopping...")
    else:
        print("No region defined. Exiting...")


if __name__ == "__main__":
    main()
