# gui.py
import os
import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from file_converter import file_to_text

class SafeCTkButton(ctk.CTkButton):
    def _draw(self, no_color_updates=False):
        try:
            super()._draw(no_color_updates=no_color_updates)
        except tk.TclError:
            # If the widget is already destroyed or invalid, we simply pass.
            pass

# Set dark mode and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class PDFOCRApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("File to Text Converter")
        self.geometry("600x500")
        self.configure(bg="#1e1e1e")
        self.file_path = None
        self.poppler_path = r"C:/Program Files/poppler-24.08.0/Library/bin"  # Adjust as needed (for PDFs)
        self.main_screen()

    def main_screen(self):
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(self, text="File to Text Converter", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        # Drop area frame
        self.drop_frame = ctk.CTkFrame(self, width=350, height=120, corner_radius=10)
        self.drop_frame.pack(pady=10)
        self.drop_frame.pack_propagate(False)

        self.drop_label = ctk.CTkLabel(self.drop_frame, text="📂 Drop File Here", font=("Arial", 18))
        self.drop_label.pack(expand=True, fill="both")
        # Bind drag-and-drop to the drop frame
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self.handle_drop)

        # Browse button
        self.browse_btn = SafeCTkButton(self, text="Browse File", command=self.browse_file, width=200)
        self.browse_btn.pack(pady=10)

        # Process button (disabled until a file is selected)
        self.process_btn = SafeCTkButton(self, text="Process", command=self.start_processing, width=200, state="disabled")
        self.process_btn.pack(pady=10)

    def show_processing_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = ctk.CTkLabel(self, text="Processing File...", font=("Arial", 22, "bold"))
        label.pack(pady=20)

        self.progress_bar = ctk.CTkProgressBar(self, width=350)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.progress_label = ctk.CTkLabel(self, text="Starting...", font=("Arial", 16))
        self.progress_label.pack(pady=5)

    def update_progress(self, current, total):
        percentage = current / total  # For CTkProgressBar, value between 0 and 1
        self.progress_bar.set(percentage)
        self.progress_label.configure(text=f"Processing Page {current} of {total}")
        self.update_idletasks()

    def handle_drop(self, event):
        file_path = event.data.strip('{}')
        # Accept multiple types: PDF, images, PPTX, DOCX
        if os.path.splitext(file_path)[1].lower() in [".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".pptx", ".docx", ".doc"]:
            self.file_path = file_path
            self.process_btn.configure(state="normal")
        else:
            messagebox.showerror("Error", "Unsupported file type!")

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Supported Files", "*.pdf *.jpg *.jpeg *.png *.tiff *.bmp *.pptx *.docx *.doc")])
        if file_path:
            self.file_path = file_path
            self.process_btn.configure(state="normal")

    def start_processing(self):
        if self.file_path:
            threading.Thread(target=self.process_file, daemon=True).start()

    def process_file(self):
        self.show_processing_screen()
        try:
            extracted_text = file_to_text(self.file_path, self.poppler_path, progress_callback=self.update_progress)
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            output_text_file = f"{base_name}.txt"
            with open(output_text_file, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            messagebox.showinfo("Success", f"Text extracted and saved as: {output_text_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.main_screen()

if __name__ == "__main__":
    app = PDFOCRApp()
    app.mainloop()
