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
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray

# Function to extract text from an image
def extract_text_from_image(image_path):
    processed_img = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_img)
    return text

# Function to process PDF in a separate thread
def pdf_to_text(pdf_path, progress_var, progress_label, start_button):
    start_button.config(state=tk.DISABLED)  # Disable start button during processing

    if not os.path.exists(pdf_path):
        messagebox.showerror("Error", "Invalid file selected!")
        start_button.config(state=tk.NORMAL)
        return

    poppler_path = r"C:/Program Files/poppler-24.08.0/Library/bin"  # Update for your system
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_text_file = f"{base_name}.txt"

    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
    
    # Create output directory
    output_dir = "pdf_pages"
    os.makedirs(output_dir, exist_ok=True)

    extracted_text = ""

    # Update progress UI
    total_pages = len(images)
    progress_var.set(0)
    progress_label.config(text="Processing pages...")

    # Process pages
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"page_{i+1}.jpg")
        image.save(image_path, "JPEG")

        # Extract text from the image
        page_text = extract_text_from_image(image_path)
        extracted_text += f"\n\n--- Page {i+1} ---\n\n{page_text}"

        # Update progress bar
        progress_var.set((i + 1) / total_pages * 100)
        progress_label.config(text=f"Processing Page {i+1}/{total_pages}")
        progress_label.update_idletasks()

    # Save extracted text to a file
    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    # Delete temporary images
    for image_file in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, image_file))
    os.rmdir(output_dir)

    # Show completion message
    messagebox.showinfo("Success", f"Text extracted and saved as: {output_text_file}")
    progress_label.config(text="Processing Complete!")
    start_button.config(state=tk.NORMAL)

# GUI Application
class PDFOCRApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("PDF to Text Converter")
        self.geometry("400x300")
        self.configure(bg="white")

        label = tk.Label(self, text="Drag and drop a PDF here or click to browse", bg="white", font=("Arial", 12))
        label.pack(pady=10)

        self.drop_area = tk.Label(self, text="📂 Drop PDF Here", bg="#f0f0f0", relief="solid", width=30, height=3, font=("Arial", 12))
        self.drop_area.pack(pady=5)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind("<<Drop>>", self.handle_drop)

        self.browse_btn = tk.Button(self, text="Browse PDF", command=self.browse_file, font=("Arial", 10), bg="#007bff", fg="white")
        self.browse_btn.pack(pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=100, length=300)
        self.progress_bar.pack(pady=5)

        self.progress_label = tk.Label(self, text="", font=("Arial", 10), bg="white")
        self.progress_label.pack(pady=5)

    def handle_drop(self, event):
        file_path = event.data.strip('{}')  # Remove curly braces
        if file_path.lower().endswith(".pdf"):
            threading.Thread(target=pdf_to_text, args=(file_path, self.progress_var, self.progress_label, self.browse_btn), daemon=True).start()
        else:
            messagebox.showerror("Error", "Only PDF files are allowed!")

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            threading.Thread(target=pdf_to_text, args=(file_path, self.progress_var, self.progress_label, self.browse_btn), daemon=True).start()

# Run the GUI
if __name__ == "__main__":
    app = PDFOCRApp()
    app.mainloop()
