import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from datetime import datetime
import os
import time
import pygame
from gtts import gTTS
import threading
import logging
from PIL import Image, ImageTk, ImageDraw

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("محول النص إلى صوت - Text to Speech Converter")
        self.root.geometry("800x600")
        self.root.configure(bg='#2e2e2e')

        # تعديل الخطوط
        self.default_font = ('Arial', 12)
        self.title_font = ('Arial', 16, 'bold')

        # إطار النصوص
        self.label = tk.Label(root, text="أدخل النص أو حمل ملفًا - Enter text or load a file:", bg='#2e2e2e', fg='#c0c0c0', font=self.title_font)
        self.label.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky='w')

        text_frame = tk.Frame(root, bg='#2e2e2e')
        text_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

        self.text_scroll = tk.Scrollbar(text_frame)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_entry = tk.Text(text_frame, height=15, width=80, wrap=tk.WORD, yscrollcommand=self.text_scroll.set, font=self.default_font, bg='#3c3c3c', fg='#e0e0e0', insertbackground='white')
        self.text_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_scroll.config(command=self.text_entry.yview)

        # أزرار التحكم
        self.load_file_button = tk.Button(root, text="تحميل ملف نصي - Load Text File", command=self.load_text_file, font=self.default_font, bg='#505050', fg='white', relief='flat', cursor='hand2')
        self.load_file_button.grid(row=2, column=0, padx=10, pady=5, sticky='ew')

        self.clear_text_button = tk.Button(root, text="تفريغ النص - Clear Text", command=self.clear_text, font=self.default_font, bg='#707070', fg='white', relief='flat', cursor='hand2')
        self.clear_text_button.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

        self.lang_var = tk.StringVar(root)
        self.lang_var.set('en')
        self.lang_menu = tk.OptionMenu(root, self.lang_var, 'en', 'ar', 'es', 'fr', 'de')
        self.lang_menu.config(bg='#3c3c3c', fg='#e0e0e0', font=self.default_font)
        self.lang_menu.grid(row=2, column=2, padx=10, pady=5, sticky='ew')

        self.convert_button = tk.Button(root, text="تحويل إلى صوت - Convert to Speech", command=self.start_convert_thread, font=self.default_font, bg='#606060', fg='white', relief='flat', cursor='hand2')
        self.convert_button.grid(row=2, column=3, padx=10, pady=5, sticky='ew')

        self.preview_button = tk.Button(root, text="معاينة - Preview", command=self.start_preview_thread, font=self.default_font, bg='#707070', fg='white', relief='flat', cursor='hand2')
        self.preview_button.grid(row=3, column=0, padx=10, pady=5, sticky='ew')

        self.pause_button = tk.Button(root, text="توقف مؤقت - Pause", command=self.toggle_pause, font=self.default_font, bg='#808080', fg='white', relief='flat', cursor='hand2')
        self.pause_button.grid(row=3, column=1, padx=10, pady=5, sticky='ew')

        self.cancel_button = tk.Button(root, text="إلغاء - Cancel", command=self.cancel_conversion, font=self.default_font, bg='#909090', fg='white', relief='flat', cursor='hand2')
        self.cancel_button.grid(row=3, column=2, padx=10, pady=5, sticky='ew')

        self.help_button = tk.Button(root, text="مساعدة - Help", command=self.show_help, font=self.default_font, bg='#a0a0a0', fg='white', relief='flat', cursor='hand2')
        self.help_button.grid(row=3, column=3, padx=10, pady=5, sticky='ew')

        self.status_label = tk.Label(root, text="", bg='#2e2e2e', fg='#c0c0c0', font=self.default_font)
        self.status_label.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky='ew')

        # ملصق المعلومات التفصيلية
        self.info_label = tk.Label(root, text="", justify=tk.LEFT, anchor='w', wraplength=750, bg='#2e2e2e', fg='#c0c0c0', font=self.default_font)
        self.info_label.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky='ew')

        # مؤشر التحميل
        self.spinner = ttk.Progressbar(root, mode='indeterminate')
        self.spinner.grid(row=6, column=0, columnspan=4, padx=10, pady=5)
        self.spinner.place_forget()

        # إضافة رمز المجلد
        self.folder_icon = self.create_folder_icon()
        self.folder_button = tk.Button(root, image=self.folder_icon, command=self.open_folder, bg='#2e2e2e', borderwidth=0, relief='flat')
        self.folder_button.grid(row=6, column=3, padx=10, pady=5, sticky='e')

        # تهيئة pygame mixer لتشغيل الصوت
        pygame.mixer.init()

        # إعداد تسجيل الأخطاء
        logging.basicConfig(filename='tts_errors.log', level=logging.ERROR)

        # متغيرات للتحكم في حالة التحويل
        self.conversion_in_progress = False
        self.paused = False
        self.preview_running = False  # Flag to track preview state

        # تحسين استجابة التصميم
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=1)

        # إنشاء قائمة منبثقة لصندوق النص
        self.create_text_popup_menu()

    def create_folder_icon(self):
        # رسم أيقونة مجلد بسيطة باستخدام Pillow
        size = (32, 32)
        icon = Image.new('RGBA', size, (0, 0, 0, 0))  # شفاف
        draw = ImageDraw.Draw(icon)
        draw.rectangle([4, 8, 28, 28], fill='#b0b0b0', outline='#a0a0a0')
        draw.rectangle([2, 4, 30, 8], fill='#b0b0b0', outline='#a0a0a0')
        return ImageTk.PhotoImage(icon)

    def create_text_popup_menu(self):
        self.text_popup_menu = tk.Menu(self.text_entry, tearoff=0)
        self.text_popup_menu.add_command(label="نسخ - Copy", command=self.copy_text)
        self.text_popup_menu.add_command(label="قص - Cut", command=self.cut_text)
        self.text_popup_menu.add_command(label="لصق - Paste", command=self.paste_text)
        self.text_popup_menu.add_command(label="تراجع - Undo", command=self.text_entry.edit_undo)
        self.text_popup_menu.add_command(label="إعادة - Redo", command=self.text_entry.edit_redo)
        self.text_popup_menu.add_separator()
        self.text_popup_menu.add_command(label="بحث - Find", command=self.find_text)
        self.text_popup_menu.add_command(label="استبدال - Replace", command=self.replace_text)

        self.text_entry.bind("<Button-3>", self.show_text_popup_menu)

    def show_text_popup_menu(self, event):
        self.text_popup_menu.post(event.x_root, event.y_root)

    def copy_text(self):
        self.text_entry.event_generate("<<Copy>>")

    def cut_text(self):
        self.text_entry.event_generate("<<Cut>>")

    def paste_text(self):
        self.text_entry.event_generate("<<Paste>>")

    def find_text(self):
        self.search_window = tk.Toplevel(self.root)
        self.search_window.title("بحث - Find")
        self.search_window.geometry("300x100")

        tk.Label(self.search_window, text="بحث عن: - Find:").grid(row=0, column=0, padx=10, pady=10)
        self.search_entry = tk.Entry(self.search_window, width=20)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Button(self.search_window, text="بحث - Find", command=self.perform_find).grid(row=1, column=0, columnspan=2, pady=10)

    def perform_find(self):
        self.text_entry.tag_remove('found', '1.0', tk.END)
        search_text = self.search_entry.get()
        if search_text:
            start_pos = '1.0'
            while True:
                start_pos = self.text_entry.search(search_text, start_pos, stopindex=tk.END)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(search_text)}c"
                self.text_entry.tag_add('found', start_pos, end_pos)
                start_pos = end_pos
            self.text_entry.tag_config('found', background='yellow', foreground='black')

    def replace_text(self):
        self.replace_window = tk.Toplevel(self.root)
        self.replace_window.title("استبدال - Replace")
        self.replace_window.geometry("300x150")

        tk.Label(self.replace_window, text="بحث عن: - Find:").grid(row=0, column=0, padx=10, pady=10)
        self.replace_search_entry = tk.Entry(self.replace_window, width=20)
        self.replace_search_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.replace_window, text="استبدال بـ: - Replace with:").grid(row=1, column=0, padx=10, pady=10)
        self.replace_entry = tk.Entry(self.replace_window, width=20)
        self.replace_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.replace_window, text="استبدال - Replace", command=self.perform_replace).grid(row=2, column=0, columnspan=2, pady=10)

    def perform_replace(self):
        search_text = self.replace_search_entry.get()
        replace_text = self.replace_entry.get()
        if search_text and replace_text:
            content = self.text_entry.get("1.0", tk.END)
            new_content = content.replace(search_text, replace_text)
            self.text_entry.delete("1.0", tk.END)
            self.text_entry.insert(tk.END, new_content)

    def load_text_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("ملفات نصية - Text files", "*.txt")]
        )
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_entry.delete("1.0", tk.END)
                self.text_entry.insert(tk.END, content)

    def clear_text(self):
        self.text_entry.delete("1.0", tk.END)

    def start_convert_thread(self):
        threading.Thread(target=self.convert_text_to_speech).start()

    def start_preview_thread(self):
        threading.Thread(target=self.preview_audio).start()

    def show_spinner(self):
        self.spinner.place(x=350, y=570)
        self.spinner.start()
        self.status_label.config(text="جاري التحويل - Conversion in progress...")

    def hide_spinner(self):
        self.spinner.stop()
        self.spinner.place_forget()
        self.status_label.config(text="")

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="استئناف - Resume")
            self.status_label.config(text="مؤقت متوقف - Paused")
            self.hide_spinner()
        else:
            self.pause_button.config(text="توقف مؤقت - Pause")
            self.status_label.config(text="جاري التحويل - Conversion in progress...")
            self.show_spinner()

    def cancel_conversion(self):
        self.conversion_in_progress = False
        self.status_label.config(text="تم إلغاء التحويل - Conversion cancelled")
        self.hide_spinner()

    def convert_text_to_speech(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        lang = self.lang_var.get()
        max_chars = 5000

        if not text:
            messagebox.showwarning("خطأ في الإدخال - Input Error", "الرجاء إدخال نص - Please enter some text.")
            return

        self.conversion_in_progress = True
        self.show_spinner()
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                filetypes=[("ملفات MP3 - MP3 files", "*.mp3")],
                initialfile=f"output_{timestamp}.mp3"
            )

            if not file_path:
                messagebox.showwarning("خطأ - Error", "لم يتم اختيار ملف لحفظه - No file selected to save.")
                return

            # Create and write to the output file
            with open(file_path, 'wb') as f:
                parts = [text[i:i + max_chars] for i in range(0, len(text), max_chars)]
                num_parts = len(parts)
                word_count = len(text.split())
                detailed_info = f"إجمالي الكلمات: {word_count}\nTotal words: {word_count}\nإجمالي الأجزاء: {num_parts}\nTotal parts: {num_parts}\n"
                for i, part in enumerate(parts):
                    if not self.conversion_in_progress:
                        break
                    tts = gTTS(text=part, lang=lang)
                    tts.write_to_fp(f)
                    detailed_info += f"جاري تحويل الجزء {i + 1}/{num_parts} ({len(part.split())} كلمات)\nConverting part {i + 1}/{num_parts} ({len(part.split())} words)\n"
                    self.info_label.config(text=detailed_info)
                    self.root.update_idletasks()
                    self.status_label.config(text=f"جاري التحويل: {i + 1}/{num_parts} - Converting: {i + 1}/{num_parts}")
                    while self.paused:
                        time.sleep(0.1)

            if self.conversion_in_progress:
                self.status_label.config(text=f"التحويل مكتمل. عدد الكلمات: {word_count}")
                self.info_label.config(text=f"التحويل مكتمل. عدد الكلمات: {word_count}")
            else:
                self.status_label.config(text="تم إلغاء التحويل - Conversion cancelled")
                self.info_label.config(text="تم إلغاء التحويل - Conversion cancelled")

        except Exception as e:
            messagebox.showerror("خطأ - Error", f"حدث خطأ أثناء التحويل: {str(e)}")
            logging.error("Error during text to speech conversion", exc_info=True)
        
        finally:
            self.conversion_in_progress = False
            self.hide_spinner()
            
            # Ensure proper cleanup
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()  # Unload the music
            except Exception as e:
                logging.error("Error during cleanup: %s", str(e))
            
            # Clean up temporary files
            temp_file = "temp_preview.mp3"
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def preview_audio(self):
        if hasattr(self, 'preview_running') and self.preview_running:
            return
        
        self.preview_running = True
        text = self.text_entry.get("1.0", tk.END).strip()
        lang = self.lang_var.get()
        if not text:
            messagebox.showwarning("خطأ في الإدخال - Input Error", "الرجاء إدخال نص - Please enter some text.")
            self.preview_running = False
            return

        temp_file = "preview.mp3"
        try:
            tts = gTTS(text=text, lang=lang)
            tts.save(temp_file)
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)  # Sleep a little to avoid busy waiting

        except Exception as e:
            logging.error(f"خطأ: {e}")
            messagebox.showerror("خطأ - Error", f"حدث خطأ أثناء معاينة الصوت: {e}")
        
        finally:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()  # Ensure unloading the file
            # Ensure the file is deleted
            if os.path.exists(temp_file):
                os.remove(temp_file)
            self.preview_running = False

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            os.startfile(folder_path)

    def show_help(self):
        help_text = (
            "مرحبًا في تطبيق تحويل النص إلى صوت.\n\n"
            "إدخال نص: أدخل النص الذي تريد تحويله إلى صوت في المربع النصي.\n"
            "تحميل ملف نصي: اضغط على زر 'تحميل ملف نصي' لاختيار ملف نصي من جهاز الكمبيوتر الخاص بك.\n"
            "تفريغ النص: اضغط على زر 'تفريغ النص' لمسح النص الحالي في المربع النصي.\n"
            "اختيار اللغة: استخدم قائمة اختيار اللغة لتحديد اللغة التي تريد تحويل النص إليها.\n"
            "تحويل إلى صوت: اضغط على زر 'تحويل إلى صوت' لتحويل النص إلى ملف صوتي بصيغة MP3.\n"
            "معاينة: اضغط على زر 'معاينة' للاستماع إلى معاينة للصوت قبل تحويل النص بالكامل.\n"
            "إيقاف مؤقت/استئناف: اضغط على زر 'توقف مؤقت' لإيقاف التحويل مؤقتًا، واضغط عليه مرة أخرى لاستئناف التحويل.\n"
            "إلغاء: اضغط على زر 'إلغاء' لإيقاف التحويل وإلغاء العملية.\n"
            "مساعدة: اضغط على زر 'مساعدة' لعرض هذه الصفحة."
        )
        messagebox.showinfo("مساعدة - Help", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
