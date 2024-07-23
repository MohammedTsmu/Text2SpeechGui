import pyttsx3
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from datetime import datetime

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech Converter")

        # Create GUI components
        self.label = tk.Label(root, text="Enter text:")
        self.label.pack(padx=10, pady=5)

        self.text_entry = tk.Text(root, height=10, width=50)
        self.text_entry.pack(padx=10, pady=5)

        self.lang_var = tk.StringVar(root)
        self.lang_var.set('en')
        self.lang_menu = tk.OptionMenu(root, self.lang_var, 'en', 'ar', 'es', 'fr', 'de')
        self.lang_menu.pack(padx=10, pady=5)

        self.speed_label = tk.Label(root, text="Select Speed:")
        self.speed_label.pack(padx=10, pady=5)

        self.speed_scale = tk.Scale(root, from_=50, to=200, orient='horizontal', label='Speed (%)', length=300)
        self.speed_scale.set(100)
        self.speed_scale.pack(padx=10, pady=5)

        self.convert_button = tk.Button(root, text="Convert to Speech", command=self.convert_text_to_speech)
        self.convert_button.pack(padx=10, pady=5)

        self.preview_button = tk.Button(root, text="Preview", command=self.preview_audio)
        self.preview_button.pack(padx=10, pady=5)

        self.help_button = tk.Button(root, text="Help", command=self.show_help)
        self.help_button.pack(padx=10, pady=5)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack(padx=10, pady=5)

        # For handling preview audio files
        self.preview_file = None
        self.engine = pyttsx3.init()  # Initialize the pyttsx3 engine

    def convert_text_to_speech(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        lang = self.lang_var.get()
        speed = self.speed_scale.get()

        if not text:
            messagebox.showwarning("Input Error", "Please enter some text.")
            return

        try:
            # Set up the pyttsx3 engine properties
            self.engine.setProperty('rate', speed)  # Set speech speed

            # Create a unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("WAV files", "*.wav")],
                initialfile=f"audio_{timestamp}.wav"
            )
            if file_path:
                self.engine.save_to_file(text, file_path)
                self.engine.runAndWait()
                self.status_label.config(text=f"Audio saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def preview_audio(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        lang = self.lang_var.get()
        speed = self.speed_scale.get()

        if not text:
            messagebox.showwarning("Input Error", "Please enter some text.")
            return

        try:
            if self.preview_file and os.path.exists(self.preview_file):
                os.remove(self.preview_file)  # Remove old preview file if it exists

            self.preview_file = f"temp_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            # Set up the pyttsx3 engine properties
            self.engine.setProperty('rate', speed)  # Set speech speed
            self.engine.save_to_file(text, self.preview_file)
            self.engine.runAndWait()

            # Play the preview file
            os.system(f"start {self.preview_file}")

            # Ensure the file is removed after playback
            os.remove(self.preview_file)
            self.preview_file = None
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_help(self):
        messagebox.showinfo("Help", "Enter text, select language, adjust speed, and click Convert to Speech or Preview.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
