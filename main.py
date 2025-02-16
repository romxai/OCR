# main.py
import sys

# Make the application DPI aware on Windows to avoid blurry scaling.
if sys.platform == "win32":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception as e:
        print("Error setting DPI awareness:", e)

import customtkinter as ctk
ctk.set_widget_scaling(1.0)  # Adjust widget scaling if necessary

from gui import PDFOCRApp

if __name__ == "__main__":
    app = PDFOCRApp()
    app.mainloop()
