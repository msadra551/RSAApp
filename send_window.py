import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
import os
import setting

class SendWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_window(parent)
        self.create_interface()
        self.apply_parent_theme()

    def setup_window(self, parent):
        self.parent = parent
        self.title(parent.translate("send"))
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)
        
        try:
            self.iconbitmap("ico/file.ico")
        except:
            pass
            
        w, h = 720, 520
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.safe_close)

    def create_interface(self):
        self.create_description()
        self.create_file_controls()
        self.create_text_area()
        self.create_action_button()

    def create_description(self):
        ctk.CTkLabel(self, text=self.parent.translate("send_desc"))\
            .grid(row=0, column=0, padx=12, pady=(12, 4), sticky="w")

    def create_file_controls(self):
        control_row = ctk.CTkFrame(self, fg_color="transparent")
        control_row.grid(row=1, column=0, sticky="ew", padx=12, pady=6)
        control_row.grid_columnconfigure(3, weight=1)
        
        self.selected_file_path = tk.StringVar(value="")
        
        ctk.CTkButton(
            control_row, 
            text=self.parent.translate("pick_file"),
            command=self.select_file
        ).grid(row=0, column=0, padx=(0, 8))
        
        ctk.CTkButton(
            control_row, 
            text=self.parent.translate("read_file"),
            command=self.read_file_content
        ).grid(row=0, column=1, padx=8)
        
        ctk.CTkLabel(
            control_row, 
            textvariable=self.selected_file_path, 
            text_color=("gray20", "#bbb")
        ).grid(row=0, column=2, sticky="w")

    def create_text_area(self):
        self.text_area = ctk.CTkTextbox(self, height=320)
        self.text_area.grid(row=2, column=0, sticky="nsew", padx=12, pady=6)

    def create_action_button(self):
        ctk.CTkButton(
            self, 
            text=self.parent.translate("encrypt_save"),
            fg_color=setting.primary_bg, 
            hover_color=setting.primary_abg,
            command=self.encrypt_and_save_message
        ).grid(row=3, column=0, padx=12, pady=10, sticky="e")

    def select_file(self):
        try:
            file_path = filedialog.askopenfilename(
                title=self.parent.translate("pick_file"),
                filetypes=[
                    ("Text / PDF / DOCX", "*.txt *.pdf *.docx *.dox"), 
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return
                
            if not setting.is_supported_file(file_path):
                self.show_error("only_formats")
                return
                
            self.selected_file_path.set(file_path)
            
        except Exception as e:
            print(f"خطا در select_file: {e}")

    def read_file_content(self):
        try:
            file_path = self.selected_file_path.get().strip()
            if not file_path:
                self.show_notice("pick_first")
                return
            
            content = setting.read_text_any(file_path)
            
            if self.winfo_exists():
                self.text_area.delete("1.0", "end")
                self.text_area.insert("1.0", content)
                
        except ImportError as ie:
            self.show_warning(str(ie))
        except Exception as e:
            self.show_error(str(e))

    def get_message_content(self):
        if not self.winfo_exists():
            return ""
        return self.text_area.get("1.0", "end").rstrip("\n")

    def encrypt_and_save_message(self):
        try:
            if not self.winfo_exists():
                return
                
            message = self.get_message_content()
            if not message:
                self.show_notice("empty_text")
                return

            output_path = self.get_save_location()
            if not output_path:
                return
                
            if not setting.is_supported_file(output_path):
                self.show_error("only_formats")
                return

            rsa_instance = self.parent.rsa
            if not rsa_instance.is_keys_generated():
                rsa_instance.generate_keys()

            encrypted_numbers = self.encrypt_message(message, rsa_instance)
            
            self.save_encrypted_file(output_path, encrypted_numbers)
            
            self.save_private_key_file(output_path, rsa_instance)

            self.show_success("enc_done")
            self.safe_close()
            
        except Exception as e:
            self.show_error(str(e))

    def get_save_location(self):
        return filedialog.asksaveasfilename(
            title=self.parent.translate("save_output"),
            defaultextension=".txt",
            filetypes=[
                ("Text", "*.txt"), 
                ("PDF", "*.pdf"), 
                ("Word (docx)", "*.docx"), 
                ("Word (dox)", "*.dox")
            ]
        )

    def encrypt_message(self, message, rsa_instance):
        encrypted_numbers = []
        for character in message:
            encrypted_numbers.append(pow(ord(character), rsa_instance.e, rsa_instance.n))
        return encrypted_numbers

    def save_encrypted_file(self, file_path, encrypted_numbers):
        encrypted_text = ",".join(map(str, encrypted_numbers))
        setting.write_text_as(file_path, encrypted_text)

    def save_private_key_file(self, original_path, rsa_instance):
        try:
            base_name, extension = os.path.splitext(original_path)
            key_file_path = f"{base_name}_private_key{extension}"
            key_content = f"n={rsa_instance.n}\nd={rsa_instance.d}"
            
            setting.write_text_as(key_file_path, key_content)
            
        except Exception as e:
            self.show_warning(
                self.parent.translate("key_save_fail").replace("{err}", str(e))
            )

    def show_notice(self, message_key):
        msg = CTkMessagebox(
            master=self, 
            title=self.parent.translate("notice"),
            message=self.parent.translate(message_key),
            icon="warning", 
            option_1="OK"
        )
        msg.get()

    def show_warning(self, message_text):
        msg = CTkMessagebox(
            master=self, 
            title=self.parent.translate("warning"),
            message=message_text, 
            icon="warning", 
            option_1="OK"
        )
        msg.get()

    def show_error(self, message):
        if isinstance(message, str) and message in setting.text.get(self.parent.lang, {}):
            message = self.parent.translate(message)
            
        msg = CTkMessagebox(
            master=self, 
            title=self.parent.translate("error"),
            message=message, 
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