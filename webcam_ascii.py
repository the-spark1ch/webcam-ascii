import cv2
import numpy as np
import argparse
import sys
import time
from shutil import get_terminal_size

ASCII_CHARS = "@%#*+=-:. "

def frame_to_ascii(frame, cols=80, rows=None):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    char_ratio = 0.55
    if rows is None:
        rows = int((h / w) * cols * char_ratio)
        rows = max(10, rows)
    small = cv2.resize(gray, (cols, rows), interpolation=cv2.INTER_AREA)
    bins = np.linspace(0, 255, len(ASCII_CHARS), endpoint=False)
    indices = np.digitize(small, bins) - 1
    lines = []
    for r in range(rows):
        line_chars = [ASCII_CHARS[min(max(i, 0), len(ASCII_CHARS) - 1)] for i in indices[r]]
        lines.append("".join(line_chars))
    return "\n".join(lines)

def run_terminal(cam_index=0, target_cols=None, fps_display=True):
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("Error: cannot open camera.")
        return
    try:
        last_time = time.time()
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cols, _ = get_terminal_size(fallback=(80, 24))
            if target_cols is None:
                cols = max(40, cols - 2)
            else:
                cols = target_cols
            ascii_str = frame_to_ascii(frame, cols=cols)
            sys.stdout.write("\x1b[H\x1b[2J")
            if fps_display:
                frame_count += 1
                now = time.time()
                elapsed = now - last_time
                if elapsed >= 0.5:
                    fps = frame_count / elapsed
                    last_time = now
                    frame_count = 0
                else:
                    fps = None
                if fps is not None:
                    sys.stdout.write(f"Webcam ASCII — FPS ~ {fps:.1f}\n")
                else:
                    sys.stdout.write("Webcam ASCII\n")
            sys.stdout.write(ascii_str)
            sys.stdout.flush()
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("\nExit.")
    finally:
        cap.release()

def run_gui(cam_index=0, width_chars=80):
    try:
        import tkinter as tk
    except Exception:
        print("GUI mode requires tkinter. Falling back to terminal mode.")
        run_terminal(cam_index)
        return
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("Error: cannot open camera.")
        return
    root = tk.Tk()
    root.title("Webcam ASCII (GUI)")
    label = tk.Label(root, text="", font=("Courier", 8), justify="left")
    label.pack(fill="both", expand=True)
    running = {"on": True}
    def update():
        if not running["on"]:
            return
        ret, frame = cap.read()
        if not ret:
            root.after(30, update)
            return
        ascii_text = frame_to_ascii(frame, cols=width_chars)
        label.config(text=ascii_text)
        root.after(30, update)
    def on_close():
        running["on"] = False
        cap.release()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.after(0, update)
    root.mainloop()

def main():
    p = argparse.ArgumentParser(description="Webcam ASCII art (terminal / GUI)")
    p.add_argument("--gui", action="store_true", help="Run in GUI mode.")
    p.add_argument("--cols", type=int, help="Character column count (terminal mode).")
    p.add_argument("--cam", type=int, default=0, help="Camera index.")
    args = p.parse_args()
    if args.gui:
        run_gui(cam_index=args.cam, width_chars=args.cols or 80)
    else:
        run_terminal(cam_index=args.cam, target_cols=args.cols)

if __name__ == "__main__":
    main()
