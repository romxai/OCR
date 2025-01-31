import os
import threading
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog, messagebox, ttk

# Set path to Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Function to process images for OCR
def preprocess_image(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    return gray

# Function to extract text from an image
def extract_text_from_image(image):
    processed_img = preprocess_image(image)
    text = pytesseract.image_to_string(processed_img)
    return text

# Function to process PDF in a separate thread
def pdf_to_text(pdf_path, app):
    app.show_processing_screen()

    if not os.path.exists(pdf_path):
        messagebox.showerror("Error", "Invalid file selected!")
        app.show_main_screen()
        return

    poppler_path = r"C:/Program Files/poppler-24.08.0/Library/bin"
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_text_file = f"{base_name}.txt"

    images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
    extracted_text_list = []

    total_pages = len(images)
    for i, image in enumerate(images):
        page_text = extract_text_from_image(image)
        extracted_text_list.append(f"\n\n--- Page {i+1} ---\n\n{page_text}")

        app.update_progress(i + 1, total_pages)

    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write("".join(extracted_text_list))

    messagebox.showinfo("Success", f"Text extracted and saved as: {output_text_file}")
    app.show_main_screen()

# GUI Application
class PDFOCRApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF to Text Converter")
        self.geometry("500x400")
        self.configure(bg="#f4f4f4")

        self.pdf_path = None
        self.main_screen()

    def main_screen(self):
        """Show the main screen with file selection."""
        for widget in self.winfo_children():
            widget.destroy()

        title = tk.Label(self, text="PDF to Text Converter", font=("Arial", 16, "bold"), bg="#f4f4f4", fg="#333")
        title.pack(pady=10)

        self.drop_area = tk.Label(self, text="📂 Drop PDF Here", bg="#ddd", relief="solid", width=30, height=3, font=("Arial", 12))
        self.drop_area.pack(pady=10)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.handle_drop)

        self.browse_btn = ttk.Button(self, text="Browse PDF", command=self.browse_file)
        self.browse_btn.pack(pady=10)

        self.process_btn = ttk.Button(self, text="Process", command=self.start_processing, state=tk.DISABLED)
        self.process_btn.pack(pady=10)

    def show_processing_screen(self):
        """Show the processing screen with progress updates."""
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Processing PDF...", font=("Arial", 14, "bold"), bg="#f4f4f4", fg="#333")
        label.pack(pady=20)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100, length=300)
        self.progress_bar.pack(pady=10)

        self.progress_label = tk.Label(self, text="Starting...", font=("Arial", 10), bg="#f4f4f4")
        self.progress_label.pack(pady=5)

    def update_progress(self, current, total):
        """Update the progress bar and label."""
        percentage = (current / total) * 100
        self.progress_var.set(percentage)
        self.progress_label.config(text=f"Processing Page {current}/{total}")
        self.update_idletasks()

    def handle_drop(self, event):
        """Handle drag-and-drop functionality."""
        file_path = event.data.strip('{}')
        if file_path.lower().endswith(".pdf"):
            self.pdf_path = file_path
            self.process_btn.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Error", "Only PDF files are allowed!")

    def browse_file(self):
        """Handle file browsing."""
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_path = file_path
            self.process_btn.config(state=tk.NORMAL)

    def start_processing(self):
        """Start the OCR process."""
        if self.pdf_path:
            threading.Thread(target=pdf_to_text, args=(self.pdf_path, self), daemon=True).start()

# Run the GUI
if __name__ == "__main__":
    app = PDFOCRApp()
    app.mainloop()
