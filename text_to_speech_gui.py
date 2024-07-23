from gtts import gTTS
import pygame
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from datetime import datetime
import time

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

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
    def convert_text_to_speech(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        lang = self.lang_var.get()

        if not text:
            messagebox.showwarning("Input Error", "Please enter some text.")
            return

        try:
            tts = gTTS(text=text, lang=lang)
            # Save the audio file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                filetypes=[("MP3 files", "*.mp3")],
                initialfile=f"audio_{timestamp}.mp3"
            )
            if file_path:
                tts.save(file_path)
                self.status_label.config(text=f"Audio saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def preview_audio(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        lang = self.lang_var.get()

        if not text:
            messagebox.showwarning("Input Error", "Please enter some text.")
            return

        try:
            if self.preview_file and os.path.exists(self.preview_file):
                os.remove(self.preview_file)  # Remove old preview file if it exists

            self.preview_file = f"temp_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            tts = gTTS(text=text, lang=lang)
            tts.save(self.preview_file)

            pygame.mixer.music.load(self.preview_file)
            pygame.mixer.music.play()

            # Wait for the playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # Ensure pygame stops playing before attempting to delete the file
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()  # Unload the file from mixer

            # Wait a bit to ensure the file is released
            time.sleep(0.5)
            if os.path.exists(self.preview_file):
                os.remove(self.preview_file)
            self.preview_file = None
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_help(self):
        messagebox.showinfo("Help", "Enter text, select language, and click Convert to Speech or Preview.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
