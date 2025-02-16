import os
import threading
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Set path to Tesseract-OCR
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Set dark appearance mode for CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")  # You can change the theme if desired

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

# GUI Application using CustomTkinter (with TkinterDnD for drag-and-drop support)
class PDFOCRApp(TkinterDnD.Tk):
    def __init__(self):
        # Inherit from TkinterDnD.Tk to enable drag-and-drop
        super().__init__()
        self.title("PDF to Text Converter")
        self.geometry("500x400")
        self.configure(bg="#1e1e1e")
        self.pdf_path = None
        self.main_screen()

    def main_screen(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Title label
        title = ctk.CTkLabel(self, text="PDF to Text Converter", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        # Drop area frame (using CTkFrame)
        self.drop_frame = ctk.CTkFrame(self, width=350, height=120, corner_radius=10)
        self.drop_frame.pack(pady=10)
        self.drop_frame.pack_propagate(False)

        # Drop area label inside the frame
        self.drop_label = ctk.CTkLabel(self.drop_frame, text="📂 Drop PDF Here", font=("Arial", 18))
        self.drop_label.pack(expand=True, fill="both")
        # Register drag-and-drop events on the drop frame (since CTkFrame is a tk.Frame subclass)
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self.handle_drop)

        # Browse button
        self.browse_btn = ctk.CTkButton(self, text="Browse PDF", command=self.browse_file, width=200)
        self.browse_btn.pack(pady=10)

        # Process button (initially disabled)
        self.process_btn = ctk.CTkButton(self, text="Process", command=self.start_processing, width=200, state="disabled")
        self.process_btn.pack(pady=10)

    def show_processing_screen(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Processing label
        label = ctk.CTkLabel(self, text="Processing PDF...", font=("Arial", 22, "bold"))
        label.pack(pady=20)

        # Progress bar (CTkProgressBar expects a value between 0 and 1)
        self.progress_bar = ctk.CTkProgressBar(self, width=350)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        # Progress text label
        self.progress_label = ctk.CTkLabel(self, text="Starting...", font=("Arial", 16))
        self.progress_label.pack(pady=5)

    def update_progress(self, current, total):
        percentage = current / total
        self.progress_bar.set(percentage)
        self.progress_label.configure(text=f"Processing Page {current} of {total}")
        self.update_idletasks()

    def handle_drop(self, event):
        # Get file path from event data and enable process button if valid
        file_path = event.data.strip('{}')
        if file_path.lower().endswith(".pdf"):
            self.pdf_path = file_path
            self.process_btn.configure(state="normal")
        else:
            messagebox.showerror("Error", "Only PDF files are allowed!")

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_path = file_path
            self.process_btn.configure(state="normal")

    def start_processing(self):
        if self.pdf_path:
            threading.Thread(target=pdf_to_text, args=(self.pdf_path, self), daemon=True).start()

# Run the GUI
if __name__ == "__main__":
    app = PDFOCRApp()
    app.mainloop()
