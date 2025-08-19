import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
import setting
from myrsa import RSA
import threading

class ProgressWindow(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.setup_progress_window(parent, title, message)
        self.create_progress_elements(message)
        self.apply_parent_theme(parent)

    def setup_progress_window(self, parent, title, message):
        self.parent = parent
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        
        w, h = 300, 120
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        self.protocol("WM_DELETE_WINDOW", self.safe_close)

    def create_progress_elements(self, message):
        frame = ctk.CTkFrame(self, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        ctk.CTkLabel(frame, text=message).pack(pady=(10, 20))
        
        self.progress_bar = ctk.CTkProgressBar(frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)

    def update_progress_value(self, value):
        try:
            if self.winfo_exists():
                self.progress_bar.set(value)
                self.update_idletasks()
        except:
            pass

    def apply_parent_theme(self, parent):
        try:
            if hasattr(parent, 'custom_colors') and parent.custom_colors["bg"]:
                bg = parent.custom_colors["bg"]
                self.configure(fg_color=bg)
        except:
            pass

    def safe_close(self):
        try:
            if self.grab_current() == self:
                self.grab_release()
            self.destroy()
        except:
            pass

class ShowWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_window(parent)
        self.create_interface()
        self.apply_parent_theme()

    def setup_window(self, parent):
        self.parent = parent
        self.title(parent.translate("show"))
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)
        
        w, h = 720, 520
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.safe_close)

    def create_interface(self):
        self.create_key_file_row()
        self.create_message_file_row()
        self.create_text_display_area()
        self.create_export_button()

    def create_key_file_row(self):
        key_row = ctk.CTkFrame(self, fg_color="transparent")
        key_row.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        
        self.key_file_path = tk.StringVar(value="")
        
        ctk.CTkButton(
            key_row, 
            text=self.parent.translate("pick_key"),
            command=self.select_key_file
        ).pack(side="left")
        
        ctk.CTkLabel(
            key_row, 
            textvariable=self.key_file_path, 
            text_color=("gray20", "#bbb")
        ).pack(side="left", padx=8)

    def create_message_file_row(self):
        message_row = ctk.CTkFrame(self, fg_color="transparent")
        message_row.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        
        self.message_file_path = tk.StringVar(value="")
        
        ctk.CTkButton(
            message_row, 
            text=self.parent.translate("pick_msg"),
            command=self.select_message_file
        ).pack(side="left")
        
        ctk.CTkButton(
            message_row, 
            text=self.parent.translate("read_show"),
            command=self.read_and_display_message
        ).pack(side="left", padx=8)
        
        ctk.CTkLabel(
            message_row, 
            textvariable=self.message_file_path, 
            text_color=("gray20", "#bbb")
        ).pack(side="left", padx=8)

    def create_text_display_area(self):
        self.text_display = ctk.CTkTextbox(self, height=360)
        self.text_display.grid(row=2, column=0, sticky="nsew", padx=12, pady=6)

    def create_export_button(self):
        ctk.CTkButton(
            self, 
            text=self.parent.translate("export"),
            fg_color=setting.primary_bg, 
            hover_color=setting.primary_abg,
            command=self.export_displayed_text
        ).grid(row=3, column=0, padx=12, pady=10, sticky="e")

    def select_key_file(self):
        try:
            file_path = filedialog.askopenfilename(
                title=self.parent.translate("pick_key"),
                filetypes=[
                    ("All", "*.*"), 
                    ("Text/PDF/DOCX", "*.txt *.pdf *.docx *.dox")
                ]
            )
            if file_path:
                self.key_file_path.set(file_path)
        except Exception as e:
            print(f"خطا در select_key_file: {e}")

    def select_message_file(self):
        try:
            file_path = filedialog.askopenfilename(
                title=self.parent.translate("pick_msg"),
                filetypes=[
                    ("All", "*.*"), 
                    ("Text/PDF/DOCX", "*.txt *.pdf *.docx *.dox")
                ]
            )
            if file_path:
                self.message_file_path.set(file_path)
        except Exception as e:
            print(f"خطا در select_message_file: {e}")

    def extract_key_values(self, key_file_content):
        key_values = {}
        
        for line in key_file_content.replace("\r", "").split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip().lower()
                value = value.strip()
                
                try:
                    if value.isdigit():
                        key_values[key] = int(value)
                    else:
                        key_values[key] = int(value.replace(",", ""))
                except:
                    pass
        
        return key_values

    def read_and_display_message(self):
        try:
            if not self.winfo_exists():
                return
            
            key_path = self.key_file_path.get().strip()
            message_path = self.message_file_path.get().strip()
            
            if not key_path:
                self.show_notice("pick_key")
                return
                
            if not message_path:
                self.show_notice("pick_msg")
                return

            try:
                key_content = setting.read_text_any(key_path)
                key_values = self.extract_key_values(key_content)
            except Exception:
                key_values = {}

            try:
                message_content = setting.read_text_any(message_path)
            except Exception as e:
                self.show_error(str(e))
                return

            if "n" not in key_values or "d" not in key_values:
                self.show_info("need_private")
                self.display_text(message_content)
                return

            self.start_decryption_process(message_content, key_values)
            
        except Exception as e:
            print(f"خطا در read_and_display_message: {e}")

    def start_decryption_process(self, raw_content, key_values):
        try:
            progress_window = ProgressWindow(
                self, 
                self.parent.translate("info"), 
                self.parent.translate("decrypting")
            )
            
            self.grab_release()
            
            def decryption_thread():
                try:
                    numbers = self.parse_encrypted_numbers(raw_content)
                    
                    rsa_instance = RSA()
                    rsa_instance.n = key_values["n"]
                    rsa_instance.d = key_values["d"]
                    rsa_instance.e = key_values.get("e", 65537)
                    
                    decrypted_text = self.decrypt_with_progress(
                        numbers, rsa_instance, progress_window
                    )
                    
                    self.after(0, lambda: self.complete_decryption(
                        decrypted_text, progress_window, True
                    ))
                    
                except Exception:
                    self.after(0, lambda: self.complete_decryption(
                        raw_content, progress_window, False
                    ))

            threading.Thread(target=decryption_thread, daemon=True).start()
            
        except Exception as e:
            print(f"خطا در start_decryption_process: {e}")

    def parse_encrypted_numbers(self, content):
        numbers = []
        
        clean_content = content.replace("\n", " ").replace("\t", " ")
        
        for token in clean_content.split():
            for part in token.split(","):
                part = part.strip()
                if part:
                    numbers.append(int(part))
        
        return numbers

    def decrypt_with_progress(self, numbers, rsa_instance, progress_window):
        total_numbers = max(1, len(numbers))
        decrypted_chars = []
        chunk_size = max(1, total_numbers // 100)
        
        for i in range(0, total_numbers, chunk_size):
            chunk = numbers[i:i + chunk_size]
            
            for number in chunk:
                decrypted_chars.append(chr(pow(int(number), rsa_instance.d, rsa_instance.n)))
            
            progress = min(1.0, (i + chunk_size) / total_numbers)
            self.after(0, lambda p=progress: progress_window.update_progress_value(p))
        
        return "".join(decrypted_chars)

    def complete_decryption(self, text_content, progress_window, success):
        try:
            if progress_window and progress_window.winfo_exists():
                progress_window.safe_close()
            
            if self.winfo_exists():
                self.grab_set()
                
                self.display_text(text_content)
                
                if not success:
                    self.show_warning("dec_fail")
                    
        except Exception as e:
            print(f"خطا در complete_decryption: {e}")

    def display_text(self, text):
        if self.winfo_exists():
            self.text_display.delete("1.0", "end")
            self.text_display.insert("1.0", text)

    def export_displayed_text(self):
        try:
            if not self.winfo_exists():
                return
                
            content = self.text_display.get("1.0", "end").rstrip("\n")
            if not content:
                self.show_notice("nothing_export")
                return
            
            save_path = filedialog.asksaveasfilename(
                title=self.parent.translate("save_output"),
                defaultextension=".txt",
                filetypes=[
                    ("Text", "*.txt"), 
                    ("PDF", "*.pdf"), 
                    ("Word (docx)", "*.docx"), 
                    ("Word (dox)", "*.dox")
                ]
            )
            
            if not save_path:
                return
            
            setting.write_text_as(save_path, content)
            self.show_success("saved")
                          
        except Exception as e:
            self.show_error(str(e))

    def show_notice(self, message_key):
        msg = CTkMessagebox(
            master=self, 
            title=self.parent.translate("notice"),
            message=self.parent.translate(message_key),
            icon="warning", 
            option_1="OK"
        )
        msg.get()

    def show_info(self, message_key):
        msg = CTkMessagebox(
            master=self, 
            title=self.parent.translate("info"),
            message=self.parent.translate(message_key),
            icon="info", 
            option_1="OK"
        )
        msg.get()

    def show_warning(self, message_key):
        msg = CTkMessagebox(
            master=self, 
            title=self.parent.translate("warning"),
            message=self.parent.translate(message_key),
            icon="warning", 
            option_1="OK"
        )
        msg.get()

    def show_error(self, message_text):
        msg = CTkMessagebox(
            master=self, 
            title=self.parent.translate("error"),
            message=message_text, 
            icon="warning", 
            option_1="OK"
        )
        msg.get()

    def show_success(self, message_key):
        msg = CTkMessagebox(
            master=self, 
            title=self.parent.translate("success"),
            message=self.parent.translate(message_key),
            icon="check", 
            option_1="OK"
        )
        msg.get()

    def safe_close(self):
        try:
            if self.grab_current() == self:
                self.grab_release()
            
            try:
                self.parent.focus_set()
            except:
                pass
                
            self.destroy()
        except:
            pass

    def apply_parent_theme(self):
        try:
            if hasattr(self.parent, 'custom_colors') and self.parent.custom_colors["bg"]:
                bg = self.parent.custom_colors["bg"]
                self.configure(fg_color=bg)
                
            if hasattr(self.parent, 'fonts'):
                family = self.parent.fonts["fa"] if self.parent.lang == "fa" else self.parent.fonts["en"]
                font_tuple = (family, self.parent.fonts["size"])
                self.apply_font_to_all_widgets(self, font_tuple)
        except:
            pass

    def apply_font_to_all_widgets(self, widget, font_tuple):
        try:
            if widget.winfo_exists():
                widget.configure(font=font_tuple)
        except:
            pass
        
        try:
            if widget.winfo_exists():
                widget.configure(dropdown_font=font_tuple)
        except:
            pass
        
        try:
            for child in widget.winfo_children():
                self.apply_font_to_all_widgets(child, font_tuple)
        except:
            pass