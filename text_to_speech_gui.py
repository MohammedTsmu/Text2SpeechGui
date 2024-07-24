import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from datetime import datetime
import os
import time
import pygame
from gtts import gTTS
import threading

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech Converter")

        self.label = tk.Label(root, text="Enter text:")
        self.label.pack(padx=10, pady=5)

        self.text_entry = tk.Text(root, height=10, width=50)
        self.text_entry.pack(padx=10, pady=5)

        self.lang_var = tk.StringVar(root)
        self.lang_var.set('en')
        self.lang_menu = tk.OptionMenu(root, self.lang_var, 'en', 'ar', 'es', 'fr', 'de')
        self.lang_menu.pack(padx=10, pady=5)

        self.convert_button = tk.Button(root, text="Convert to Speech", command=self.start_convert_thread)
        self.convert_button.pack(padx=10, pady=5)

        self.preview_button = tk.Button(root, text="Preview", command=self.start_preview_thread)
        self.preview_button.pack(padx=10, pady=5)

        self.help_button = tk.Button(root, text="Help", command=self.show_help)
        self.help_button.pack(padx=10, pady=5)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack(padx=10, pady=5)

        # Spinner for loading
        self.spinner = ttk.Progressbar(root, mode='indeterminate')
        
        pygame.mixer.init()

    def start_convert_thread(self):
        threading.Thread(target=self.convert_text_to_speech).start()

    def start_preview_thread(self):
        threading.Thread(target=self.preview_audio).start()

    def show_spinner(self):
        self.spinner.pack(padx=10, pady=5)
        self.spinner.start()

    def hide_spinner(self):
        self.spinner.stop()
        self.spinner.pack_forget()

    def convert_text_to_speech(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        lang = self.lang_var.get()
        max_chars = 5000

        if not text:
            messagebox.showwarning("Input Error", "Please enter some text.")
            return

        self.show_spinner()
        try:
            parts = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                filetypes=[("MP3 files", "*.mp3")],
                initialfile=f"audio_{timestamp}.mp3"
            )
            if file_path:
                for part in parts:
                    tts = gTTS(text=part, lang=lang)
                    tts.save(file_path)
                self.status_label.config(text=f"Audio saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.hide_spinner()

    def preview_audio(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        lang = self.lang_var.get()
        max_chars = 5000

        if not text:
            messagebox.showwarning("Input Error", "Please enter some text.")
            return

        self.show_spinner()
        try:
            if hasattr(self, 'preview_file') and os.path.exists(self.preview_file):
                os.remove(self.preview_file)

            parts = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
            self.preview_file = f"temp_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            for part in parts:
                tts = gTTS(text=part, lang=lang)
                tts.save(self.preview_file)

            pygame.mixer.music.load(self.preview_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            time.sleep(0.5)
            if os.path.exists(self.preview_file):
                os.remove(self.preview_file)
            self.preview_file = None
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.hide_spinner()

    def show_help(self):
        messagebox.showinfo("Help", "1. Enter text in the 'Text' field.\n"
                                   "2. Select the language from the dropdown.\n"
                                   "3. Click 'Convert to Speech' to create an audio file.\n"
                                   "4. Use 'Preview' to listen to the generated speech.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
