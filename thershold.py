import cv2
import numpy as np
from PIL import ImageGrab
import tkinter as tk
from tkinter import Scale, Label


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


def find_and_display_match(region, template_path, threshold):
    try:
        img = ImageGrab.grab(bbox=region)
        img_np = np.array(img)
        img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

        # Load the template
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        template_np = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)

        # Perform template matching
        result = cv2.matchTemplate(img_rgb, template_np, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Draw rectangles for matches above the threshold
        img_display = img_rgb.copy()
        if max_val >= threshold:
            template_height, template_width = template_np.shape[:2]
            top_left = max_loc
            bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
            cv2.rectangle(img_display, top_left, bottom_right, (0, 255, 0), 2)

        # Display the image with matches
        cv2.imshow("Template Matching", img_display)
        cv2.waitKey(1)
    except Exception as e:
        print(f"Unexpected error: {e}")


def update_threshold(value, region, template_path):
    threshold = int(value) / 100.0
    find_and_display_match(region, template_path, threshold)


def main():
    root = tk.Tk()
    app = ScreenRegionSelector(root)
    root.mainloop()

    if app.region:
        template_path = "1.png"  # Update with your template image path

        # Create a window for threshold adjustment
        threshold_window = tk.Toplevel()
        threshold_window.title("Adjust Threshold")

        # Add a scale widget to adjust the threshold
        threshold_scale = Scale(
            threshold_window,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            label="Threshold (%)",
        )
        threshold_scale.pack()
        threshold_scale.set(70)  # Default threshold
        threshold_scale.bind(
            "<Motion>",
            lambda event: update_threshold(
                threshold_scale.get(), app.region, template_path
            ),
        )

        # Keep the window open
        threshold_window.mainloop()
    else:
        print("No region defined. Exiting...")


if __name__ == "__main__":
    main()
