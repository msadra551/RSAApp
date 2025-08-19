import customtkinter as ctk
import tkinter as tk
from tkinter import font as tkfont, colorchooser
from CTkMessagebox import CTkMessagebox
import webbrowser
from PIL import Image, ImageTk

import setting
from myrsa import RSA
from range_window import RangeWindow
from send_window import SendWindow
from show_window import ShowWindow


class RSAProgram(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.setup_initial_config()
        self.create_interface()
        self.apply_styling()

    def setup_initial_config(self):
        self.lang, self.appearance = setting.parse_cli()
        ctk.set_appearance_mode(self.appearance)
        self.title("RSA")
        self.resizable(0, 0)

        w, h = 280, 300
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.grid_columnconfigure(0, weight=1)

        self.theme_var = tk.StringVar(value=self.appearance)
        self.lang_var = tk.StringVar(value=self.lang)
        self.custom_colors = {"bg": None, "fg": None}
        self.fonts = {"size": 14, "en": "Segoe UI", "fa": "Segoe UI"}
        self.menu_font = tkfont.Font(family="Segoe UI", size=14)

        self.rsa_start, self.rsa_end = 1000, 10000
        self.rsa = RSA(self.rsa_start, self.rsa_end)

        self.open_windows = []

        try:
            self.iconbitmap(setting.icon_asset("file.ico"))
        except Exception:
            pass

    def create_interface(self):
        self.load_menu_icons()
        self.create_menus()
        self.create_menubar()
        self.create_main_buttons()
        self.protocol("WM_DELETE_WINDOW", lambda: self.cleanup_and_exit())

    def apply_styling(self):
        self.apply_menu_colors()

    def translate(self, key, en="", fa=""):
        try:
            return setting.text[self.lang].get(key, fa if self.lang == "fa" else en)
        except Exception:
            return fa if self.lang == "fa" else en

    def cleanup_and_exit(self):
        for w in self.open_windows[:]:
            try:
                if w and w.winfo_exists():
                    w.destroy()
            except Exception:
                pass
        self.open_windows.clear()
        try:
            self.destroy()
        except Exception:
            pass

    def load_menu_icons(self):
        def load_icon(path, size=(18, 18)):
            try:
                abs_path = setting.asset(path)  
                img = Image.open(abs_path).resize(size, Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception:
                return None

        self.menu_icons = {
            "flag_en":  load_icon("ico/en.ico"),
            "flag_fa":  load_icon("ico/fa.ico"),
            "email":    load_icon("ico/mail.ico"),
            "github":   load_icon("ico/Github.ico"),
            "linkedin": load_icon("ico/linkedin.ico"),
            "about":    load_icon("ico/web.ico"),
        }

    def show_algorithm_info(self):
        CTkMessagebox(
            master=self,
            title=self.translate("about_algo_menu"),
            message=self.translate("about_algo_text"),
            icon="info",
            option_1=self.translate("ok")
        )

    def show_app_info(self):
        CTkMessagebox(
            master=self,
            title=self.translate("about_app_menu"),
            message=self.translate("about_app_text"),
            icon="info",
            option_1=self.translate("ok")
        )

    def confirm_exit(self):
        msg = CTkMessagebox(
            master=self,
            title=self.translate("exit_title"),
            message=self.translate("exit_msg"),
            icon=setting.icon_asset("close.ico"),
            option_1=self.translate("no"),
            option_2=self.translate("yes")
        )
        if msg.get() == self.translate("yes"):
            self.cleanup_and_exit()

    def create_menus(self):
        self.create_settings_menu()
        self.create_about_menu()

    def create_settings_menu(self):
        self.menu_settings = tk.Menu(self, tearoff=0, font=self.menu_font)

        self.create_theme_menu()
        self.menu_settings.add_cascade(label=self.translate("themes"), menu=self.menu_themes)

        self.menu_settings.add_command(label=self.translate("fonts"), command=self.show_fonts_dialog)

        self.create_language_menu()
        self.menu_settings.add_cascade(label=self.translate("language"), menu=self.menu_lang)

        self.menu_settings.add_separator()
        self.menu_settings.add_command(label=self.translate("interval"), command=self.open_range_window)
        self.menu_settings.add_command(label=self.translate("exit"), command=self.confirm_exit)

    def create_theme_menu(self):
        self.menu_themes = tk.Menu(self.menu_settings, tearoff=0, font=self.menu_font)
        theme_labels = self.translate("theme_labels")

        for key in ("system", "light", "dark"):
            self.menu_themes.add_radiobutton(
                label=theme_labels[key],
                value=key,
                variable=self.theme_var,
                command=lambda v=key: self.change_theme(v)
            )

        self.menu_themes.add_separator()
        self.menu_themes.add_command(
            label=self.translate("theme_custom"),
            command=self.show_colors_dialog
        )

    def create_language_menu(self):
        self.menu_lang = tk.Menu(self.menu_settings, tearoff=0, font=self.menu_font)

        self.menu_lang.add_radiobutton(
            label="English",
            value="en",
            variable=self.lang_var,
            image=self.menu_icons.get("flag_en"),
            compound="left",
            command=lambda: self.switch_language("en")
        )

        self.menu_lang.add_radiobutton(
            label="فارسی",
            value="fa",
            variable=self.lang_var,
            image=self.menu_icons.get("flag_fa"),
            compound="left",
            command=lambda: self.switch_language("fa")
        )

    def create_about_menu(self):
        self.menu_about = tk.Menu(self, tearoff=0, font=self.menu_font)

        self.menu_about.add_command(
            label=self.translate("about_algo_menu"),
            command=self.show_algorithm_info
        )
        self.menu_about.add_command(
            label=self.translate("about_app_menu"),
            command=self.show_app_info
        )

        self.create_contact_menu()
        self.menu_about.add_cascade(
            label=self.translate("about_contact_menu"),
            menu=self.menu_contact
        )

    def create_contact_menu(self):
        self.menu_contact = tk.Menu(self.menu_about, tearoff=0, font=self.menu_font)
        links = getattr(setting, "contact_links", {})

        contacts = [
            ("contact_about", "about", "about"),
            ("contact_github", "github", "github"),
            ("contact_linkedin", "linkedin", "linkedin"),
            ("contact_email", "email", "email")
        ]

        for text_key, icon_key, link_key in contacts:
            url = links.get(link_key, "")
            if link_key == "email":
                url = f"mailto:{url}"

            self.menu_contact.add_command(
                label=self.translate(text_key),
                image=self.menu_icons.get(icon_key),
                compound="left",
                command=lambda u=url: self.open_link(u)
            )

    def create_menubar(self):
        self.bar = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color=("gray95", "#1f1f1f"))
        self.bar.grid(row=0, column=0, sticky="ew")
        self.bar.grid_columnconfigure(3, weight=1)

        button_style = {
            "fg_color": "transparent",
            "text_color": ("black", "white"),
            "hover_color": ("gray85", "#2a2a2a"),
            "height": 30,
            "corner_radius": 6,
            "cursor": "hand2"
        }

        self.btn_settings = ctk.CTkButton(
            self.bar, text="⚙", width=36, **button_style,
            command=lambda: self.show_menu(self.menu_settings, self.btn_settings)
        )
        self.btn_settings.grid(row=0, column=0, padx=(8, 4), pady=5)

        self.btn_about = ctk.CTkButton(
            self.bar, text=self.translate("about"), width=80, **button_style,
            command=lambda: self.show_menu(self.menu_about, self.btn_about)
        )
        self.btn_about.grid(row=0, column=1, padx=4, pady=5)

    def show_menu(self, menu, anchor):
        try:
            if anchor.winfo_exists():
                x = anchor.winfo_rootx()
                y = anchor.winfo_rooty() + anchor.winfo_height()
                menu.post(x, y)
        except Exception:
            pass

    def create_main_buttons(self):
        buttons_config = [
            ("send", self.open_send_window, setting.primary_bg, setting.primary_abg),
            ("show", self.open_show_window, setting.primary_bg, setting.primary_abg),
            ("interval", self.open_range_window, setting.succses_bg, setting.success_abg),
            ("close", self.confirm_exit, setting.close_bg, setting.close_abg)
        ]

        self.main_buttons = []

        for i, (text_key, command, bg_color, hover_color) in enumerate(buttons_config):
            btn = ctk.CTkButton(
                self,
                text=self.translate(text_key),
                fg_color=bg_color,
                hover_color=hover_color,
                corner_radius=50,
                height=38,
                cursor="hand2",
                command=command
            )
            btn.grid(row=i + 1, column=0, padx=10, pady=10, sticky="ew")

            self.main_buttons.append((btn, text_key))

    def update_main_buttons_text(self):
        for btn, text_key in self.main_buttons:
            try:
                if btn.winfo_exists():
                    btn.configure(text=self.translate(text_key))
            except Exception:
                pass

    def change_theme(self, mode):
        ctk.set_appearance_mode(mode)
        if mode in ("light", "dark", "system"):
            self.custom_colors = {"bg": None, "fg": None}
        self.apply_main_theme()
        self.apply_menu_colors()

    def apply_main_theme(self):
        if self.custom_colors["bg"]:
            bg = self.custom_colors["bg"]
            fg = self.custom_colors["fg"]

            self.configure(fg_color=bg)
            self.bar.configure(fg_color=setting.shade(bg, 0.9))

            if hasattr(self, 'btn_about'):
                self.btn_about.configure(text_color=fg)
            if hasattr(self, 'btn_settings'):
                self.btn_settings.configure(text_color=fg)

        else:
            self.configure(fg_color=("gray94", "gray14"))
            self.bar.configure(fg_color=("gray95", "#1f1f1f"))

            if hasattr(self, 'btn_about'):
                self.btn_about.configure(text_color=("black", "white"))
            if hasattr(self, 'btn_settings'):
                self.btn_settings.configure(text_color=("black", "white"))

    def show_colors_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.translate("custom_title"))
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)

        self.open_windows.append(dialog)

        w, h = 360, 170
        x = self.winfo_rootx() + (self.winfo_width() - w) // 2
        y = self.winfo_rooty() + (self.winfo_height() - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        frame = ctk.CTkFrame(dialog, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        bg_var = tk.StringVar(value=self.custom_colors["bg"] or "#101418")
        fg_var = tk.StringVar(value=self.custom_colors["fg"] or "#ffffff")

        self.create_color_row(frame, self.translate("custom_bg"), bg_var)

        self.create_color_row(frame, self.translate("custom_fg"), fg_var)

        self.create_dialog_buttons(frame, dialog, bg_var, fg_var)

        if self.custom_colors["bg"]:
            dialog.configure(fg_color=self.custom_colors["bg"])

        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_dialog(dialog))

    def create_color_row(self, parent, label_text, color_var):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=6)

        ctk.CTkLabel(row, text=label_text).pack(side="left", padx=(0, 8))
        ctk.CTkEntry(row, width=120, textvariable=color_var).pack(side="left")
        ctk.CTkButton(
            row, text=self.translate("custom_pick"), width=90,
            command=lambda: self.pick_color(color_var, label_text)
        ).pack(side="left", padx=6)

    def pick_color(self, color_var, title):
        color = colorchooser.askcolor(title=title)[1]
        if color:
            color_var.set(color)

    def create_dialog_buttons(self, parent, dialog, bg_var, fg_var):
        btns = ctk.CTkFrame(parent, fg_color="transparent")
        btns.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            btns, text=self.translate("cancel"), width=80,
            command=lambda: self.close_dialog(dialog)
        ).pack(side="right", padx=6)

        ctk.CTkButton(
            btns, text=self.translate("ok"), width=80,
            fg_color=setting.succses_bg, hover_color=setting.success_abg,
            command=lambda: self.apply_colors(dialog, bg_var, fg_var)
        ).pack(side="right")

    def apply_colors(self, dialog, bg_var, fg_var):
        bg, fg = bg_var.get().strip(), fg_var.get().strip()
        if setting.hex_ok(bg) and setting.hex_ok(fg):
            self.custom_colors = {"bg": bg, "fg": fg}
            self.apply_main_theme()
            self.apply_menu_colors()

            for window in self.open_windows:
                try:
                    if window.winfo_exists() and hasattr(window, 'apply_parent_theme'):
                        window.apply_parent_theme()
                except Exception:
                    pass

            self.close_dialog(dialog)
        else:
            CTkMessagebox(
                master=self, title=self.translate("error"),
                message="رنگ نامعتبر", icon="warning", option_1="OK"
            )

    def close_dialog(self, dialog):
        try:
            if dialog in self.open_windows:
                self.open_windows.remove(dialog)
            if dialog.winfo_exists():
                dialog.destroy()
        except Exception:
            pass

    def apply_menu_colors(self):
        if self.custom_colors["bg"] and self.custom_colors["fg"]:
            bg = self.custom_colors["bg"]
            fg = self.custom_colors["fg"]
            abg = setting.shade(bg, 0.92)
            afg = fg
        else:
            mode = ctk.get_appearance_mode().lower()
            palette = setting.paletts["dark" if mode == "dark" else "light"]
            bg, fg, abg, afg = palette["bg"], palette["fg"], palette["abg"], palette["afg"]

        menus = [
            self.menu_settings, self.menu_themes, self.menu_lang,
            self.menu_about, self.menu_contact
        ]

        for menu in menus:
            if menu:
                try:
                    menu.configure(bg=bg, fg=fg, activebackground=abg, activeforeground=afg)
                except Exception:
                    pass

    def show_fonts_dialog(self):
        installed = sorted(set(tkfont.families()))
        en_list = [f for f in getattr(setting, "en_fonts", []) if f in installed] or ["Segoe UI"]
        fa_list = [f for f in getattr(setting, "fa_fonts", []) if f in installed] or en_list

        dialog = ctk.CTkToplevel(self)
        dialog.title(self.translate("fonts_title"))
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)

        self.open_windows.append(dialog)

        w, h = 420, 220
        x = self.winfo_rootx() + (self.winfo_width() - w) // 2
        y = self.winfo_rooty() + (self.winfo_height() - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")

        frame = ctk.CTkFrame(dialog, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        ctk.CTkLabel(frame, text=self.translate("fonts_en")).pack(anchor="w")
        en_var = tk.StringVar(value=self.fonts["en"])
        ctk.CTkComboBox(frame, values=en_list, variable=en_var, width=320).pack(pady=(0, 8))

        ctk.CTkLabel(frame, text=self.translate("fonts_fa")).pack(anchor="w")
        fa_var = tk.StringVar(value=self.fonts["fa"])
        ctk.CTkComboBox(frame, values=fa_list, variable=fa_var, width=320).pack(pady=(0, 8))

        size_row = ctk.CTkFrame(frame, fg_color="transparent")
        size_row.pack(fill="x", pady=4)
        ctk.CTkLabel(size_row, text=self.translate("fonts_size")).pack(side="left")
        size_var = tk.IntVar(value=self.fonts["size"])
        ctk.CTkEntry(size_row, width=80, textvariable=size_var).pack(side="left", padx=8)

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            btns, text=self.translate("fonts_cancel"), width=80,
            command=lambda: self.close_dialog(dialog)
        ).pack(side="right", padx=6)

        ctk.CTkButton(
            btns, text=self.translate("fonts_apply"), width=80,
            fg_color=setting.primary_bg, hover_color=setting.primary_abg,
            command=lambda: self.apply_fonts(dialog, en_var, fa_var, size_var)
        ).pack(side="right")

        if self.custom_colors["bg"]:
            dialog.configure(fg_color=self.custom_colors["bg"])

        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_dialog(dialog))

    def apply_fonts(self, dialog, en_var, fa_var, size_var):
        try:
            size = max(8, min(48, int(size_var.get())))
        except Exception:
            size = self.fonts["size"]

        self.fonts.update({
            "en": en_var.get(),
            "fa": fa_var.get(),
            "size": size
        })

        self.apply_fonts_to_widgets()
        self.close_dialog(dialog)

    def apply_fonts_to_widgets(self):
        family = self.fonts["fa"] if self.lang == "fa" else self.fonts["en"]
        font_tuple = (family, self.fonts["size"])
        self.menu_font.configure(family=font_tuple[0], size=font_tuple[1])

        menus = [
            self.menu_settings, self.menu_themes, self.menu_lang,
            self.menu_about, self.menu_contact
        ]

        for menu in menus:
            if menu:
                try:
                    menu.configure(font=self.menu_font)
                except Exception:
                    pass

        self.apply_font_recursive(self, font_tuple)

    def apply_font_recursive(self, widget, font_tuple):
        try:
            if widget.winfo_exists():
                widget.configure(font=font_tuple)

                if self.custom_colors["fg"] and hasattr(widget, 'configure'):
                    try:
                        if any(widget_type in str(type(widget)).lower()
                               for widget_type in ['label', 'button']):
                            widget.configure(text_color=self.custom_colors["fg"])
                    except Exception:
                        pass
        except Exception:
            pass

        try:
            if widget.winfo_exists():
                widget.configure(dropdown_font=font_tuple)
        except Exception:
            pass

        try:
            for child in widget.winfo_children():
                self.apply_font_recursive(child, font_tuple)
        except Exception:
            pass

    def open_link(self, url):
        try:
            webbrowser.open(url)
        except Exception:
            pass

    def switch_language(self, lang):
        self.lang = lang
        self.lang_var.set(lang)
        self.update_ui_texts()
        self.apply_fonts_to_widgets()

    def update_ui_texts(self):
        try:
            self.btn_about.configure(text=self.translate("about"))
            self.update_main_buttons_text()
            self.create_menus()
            self.apply_menu_colors()
        except Exception:
            pass

    def open_child_window(self, window_class):
        try:
            window = window_class(self)
            self.open_windows.append(window)
            window.protocol("WM_DELETE_WINDOW", lambda: self.close_child_window(window))
        except Exception as e:
            print(f"خطا در باز کردن پنجره: {e}")

    def open_send_window(self):
        self.open_child_window(SendWindow)

    def open_show_window(self):
        self.open_child_window(ShowWindow)

    def open_range_window(self):
        self.open_child_window(RangeWindow)

    def close_child_window(self, window):
        try:
            if window in self.open_windows:
                self.open_windows.remove(window)
            if window.winfo_exists():
                window.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    RSAProgram().mainloop()
