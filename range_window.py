import customtkinter as ctk
import tkinter as tk
from CTkMessagebox import CTkMessagebox

class RangeWindow(ctk.CTkToplevel):
    MAX_END = 1_000_000

    def __init__(self, parent):
        super().__init__(parent)
        self.setup_window(parent)
        self.create_interface()
        self.apply_parent_theme()

    def setup_window(self, parent):
        self.parent = parent
        self.title(parent.translate("interval_title"))
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        
        w, h = 360, 160
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self.safe_close)

    def create_interface(self):
        frame = ctk.CTkFrame(self, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        self.start_var = tk.StringVar(value=str(self.parent.rsa_start))
        self.end_var = tk.StringVar(value=str(self.parent.rsa_end))

        self.create_input_fields(frame)
        
        self.create_buttons(frame)

    def create_input_fields(self, parent):
        start_row = ctk.CTkFrame(parent, fg_color="transparent")
        start_row.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            start_row, 
            text=f"{self.parent.translate('interval_start')} ({self.parent.translate('interval_start_hint')})"
        ).pack(side="left")
        ctk.CTkEntry(start_row, width=120, textvariable=self.start_var).pack(side="left", padx=8)

        end_row = ctk.CTkFrame(parent, fg_color="transparent")
        end_row.pack(fill="x", pady=6)
        
        ctk.CTkLabel(
            end_row, 
            text=f"{self.parent.translate('interval_end')} ({self.parent.translate('interval_end_hint')})"
        ).pack(side="left")
        ctk.CTkEntry(end_row, width=120, textvariable=self.end_var).pack(side="left", padx=8)

    def create_buttons(self, parent):
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            buttons_frame, 
            text=self.parent.translate("cancel"), 
            width=80,
            command=self.safe_close
        ).pack(side="right", padx=6)

        ctk.CTkButton(
            buttons_frame, 
            text=self.parent.translate("save"), 
            width=80,
            command=self.save_range
        ).pack(side="right")

    def validate_inputs(self):
        try:
            start = int(self.start_var.get())
            end = int(self.end_var.get())
        except ValueError:
            self.show_error("interval_err_int")
            return None, None
        
        if start < 2:
            self.show_error("interval_err_start")
            return None, None
        
        if end <= start + 5:
            self.show_error("interval_err_gap")
            return None, None
        
        if end > self.MAX_END:
            self.show_error("interval_err_max")
            return None, None
        
        return start, end

    def save_range(self):
        try:
            if not self.winfo_exists():
                return
                
            start, end = self.validate_inputs()
            if start is None or end is None:
                return

            self.parent.rsa_start = start
            self.parent.rsa_end = end
            self.parent.rsa.set_prime_range(start, end)
            
            self.show_success("interval_saved")
            self.safe_close()
            
        except Exception as e:
            print(f"خطا در save_range: {e}")

    def show_error(self, message_key):
        msg = CTkMessagebox(
            master=self.parent, 
            title=self.parent.translate("error"),
            message=self.parent.translate(message_key),
            icon="warning", 
            option_1="OK"
        )
        msg.get()  

    def show_success(self, message_key):
        msg = CTkMessagebox(
            master=self.parent, 
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