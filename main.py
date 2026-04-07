import customtkinter as ctk
import ctypes
import json
import os
from config import COLORS, DWMWA_USE_IMMERSIVE_DARK_MODE, DWMWA_CAPTION_COLOR, DEFAULT_SETTINGS, SETTINGS_FILE
from ui import CustomDropdown, GlowButton, SidebarButton, AnimationMixin
from ui.pages import DorkingPage, SettingsPage, ComingSoonPage, PhoneCheckPage
try:
    from BlurWindow.blurWindow import blur
    BLUR_AVAILABLE = True
except ImportError:
    BLUR_AVAILABLE = False
    print("BlurWindow not installed. Install with: pip install BlurWindow")
class TriumphOSINT(AnimationMixin):
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Triumphoby OSINT")
        self.root.geometry("1200x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.settings_file = SETTINGS_FILE
        self.load_settings()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.apply_dark_title_bar()
        self.transitioning = False
        self.dorking_page = None
        self.settings_page = None
        self.build_ui()
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = DEFAULT_SETTINGS.copy()
        except:
            self.settings = DEFAULT_SETTINGS.copy()
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            print("Settings saved!")
        except Exception as e:
            print(f"Failed to save settings: {e}")
    def on_closing(self):
        self.root.destroy()
    def apply_dark_title_bar(self):
        try:
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int)
            )
            color = 0x001a1212
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_CAPTION_COLOR,
                ctypes.byref(ctypes.c_int(color)), ctypes.sizeof(ctypes.c_int)
            )
            blur_type = self.settings.get('blur_type', 'Standard')
            if blur_type == "None":
                try:
                    self.root.attributes('-alpha', 1.0)
                    DWM_BLURBEHIND = 20
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, DWM_BLURBEHIND,
                        ctypes.byref(ctypes.c_int(0)), ctypes.sizeof(ctypes.c_int)
                    )
                    print("Blur disabled - solid background")
                except Exception as e:
                    print(f"Failed to disable blur: {e}")
            elif BLUR_AVAILABLE:
                try:
                    if blur_type == "Standard":
                        blur(hwnd, Acrylic=False, Dark=True)
                        print(f"Blur effect applied: {blur_type}")
                    elif blur_type == "Acrylic":
                        blur(hwnd, Acrylic=True, Dark=True)
                        print(f"Blur effect applied: {blur_type}")
                except Exception as e:
                    print(f"BlurWindow error: {e}")
            else:
                print("BlurWindow not available")
        except Exception as e:
            print(f"Window effects failed: {e}")
    def build_ui(self):
        try:
            opacity = self.settings.get('bg_opacity', self.settings.get('transparency', 0.95))
            self.root.attributes('-alpha', opacity)
        except:
            pass
        self.root.configure(fg_color=COLORS['bg'])
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        sidebar = self.create_sidebar(main_container)
        sidebar.pack(side="left", fill="y", padx=0)
        content_wrapper = ctk.CTkFrame(
            main_container,
            corner_radius=0,
            fg_color=COLORS['bg'],
            border_width=0
        )
        content_wrapper.pack(side="right", fill="both", expand=True)
        self.breadcrumb_frame = ctk.CTkFrame(
            content_wrapper,
            corner_radius=0,
            fg_color=COLORS['surface_solid'],
            border_width=0,
            height=40
        )
        self.breadcrumb_frame.pack(fill="x", side="top")
        self.breadcrumb_frame.pack_propagate(False)
        breadcrumb_bg = ctk.CTkFrame(
            self.breadcrumb_frame,
            fg_color=COLORS['bg'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        breadcrumb_bg.pack(side="left", padx=20, pady=8)
        self.breadcrumb_label = ctk.CTkLabel(
            breadcrumb_bg,
            text="Triumphoby",
            font=("Segoe UI", 10),
            text_color=COLORS['text_dim'],
            anchor="w"
        )
        self.breadcrumb_label.pack(padx=12, pady=6)
        self.content_frame = ctk.CTkFrame(
            content_wrapper,
            corner_radius=0,
            fg_color="transparent",
            border_width=0
        )
        self.content_frame.pack(fill="both", expand=True)
        self.show_welcome()
    def create_sidebar(self, parent):
        sidebar = ctk.CTkFrame(
            parent,
            width=240,
            corner_radius=0,
            fg_color=COLORS['surface_solid'],
            border_width=0
        )
        sidebar.pack_propagate(False)
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=(25, 20))
        logo = ctk.CTkLabel(
            logo_frame,
            text="TRIUMPHOBY",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS['accent']
        )
        logo.pack()
        subtitle = ctk.CTkLabel(
            logo_frame,
            text="OSINT Suite",
            font=("Segoe UI", 9),
            text_color=COLORS['text_darker']
        )
        subtitle.pack(pady=(2, 0))
        separator = ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['border'])
        separator.pack(fill="x", padx=20, pady=(2, 0))
        self.sidebar_buttons = {}
        self.sidebar_buttons['dorking'] = SidebarButton(
            sidebar, "Dorking", command=lambda: self.transition_to_page(self.show_dorking_content)
        )
        self.sidebar_buttons['dorking'].pack(fill="x", padx=12, pady=1.5)
        self.sidebar_buttons['namesearch'] = SidebarButton(
            sidebar, "Name Search", command=lambda: self.transition_to_page(self.show_namesearch_content)
        )
        self.sidebar_buttons['namesearch'].pack(fill="x", padx=12, pady=1.5)
        self.sidebar_buttons['phonecheck'] = SidebarButton(
            sidebar, "Phone Check", command=lambda: self.transition_to_page(self.show_phonecheck_content)
        )
        self.sidebar_buttons['phonecheck'].pack(fill="x", padx=12, pady=1.5)
        spacer = ctk.CTkFrame(sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)
        self.sidebar_buttons['settings'] = SidebarButton(
            sidebar, "Settings", command=lambda: self.transition_to_page(self.show_settings_content)
        )
        self.sidebar_buttons['settings'].pack(fill="x", padx=12, pady=1.5)
        info_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        info_frame.pack(side="bottom", fill="x", padx=15, pady=15)
        ctk.CTkLabel(
            info_frame,
            text="v1.0.0",
            font=("Segoe UI", 9),
            text_color=COLORS['text_darker']
        ).pack()
        return sidebar
    def update_breadcrumb(self, path):
        self.breadcrumb_label.configure(text=path)
    def show_welcome(self):
        self.update_breadcrumb("Triumphoby")
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        welcome_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        welcome_frame.place(relx=0.5, rely=0.5, anchor="center")
        title = ctk.CTkLabel(
            welcome_frame,
            text="Triumphoby",
            font=("Segoe UI", 28),
            text_color=COLORS['text']
        )
        title.pack(pady=(0, 8))
        subtitle = ctk.CTkLabel(
            welcome_frame,
            text="Select a module to begin",
            font=("Segoe UI", 12),
            text_color=COLORS['text_dim']
        )
        subtitle.pack()
    def show_coming_soon_content(self, module):
        self.update_breadcrumb(f"Triumphoby / {module}")
        for btn in self.sidebar_buttons.values():
            btn.set_active(False)
        page = ComingSoonPage(self.content_frame, module)
        page.render()
    def show_settings_content(self):
        self.update_breadcrumb("Triumphoby / Settings")
        for btn in self.sidebar_buttons.values():
            btn.set_active(False)
        self.sidebar_buttons['settings'].set_active(True)
        self.settings_page = SettingsPage(self.content_frame, self)
        self.settings_page.show()
    def show_dorking_content(self):
        self.update_breadcrumb("Triumphoby / Dorking")
        for btn in self.sidebar_buttons.values():
            btn.set_active(False)
        self.sidebar_buttons['dorking'].set_active(True)
        if not self.dorking_page:
            self.dorking_page = DorkingPage(self.content_frame, self)
        self.dorking_page.show()
    def show_namesearch_content(self):
        self.update_breadcrumb("Triumphoby / Name Search")
        for btn in self.sidebar_buttons.values():
            btn.set_active(False)
        self.sidebar_buttons['namesearch'].set_active(True)
        if not hasattr(self, 'namesearch_page') or not self.namesearch_page:
            from ui.pages import NameSearchPage
            self.namesearch_page = NameSearchPage(self.content_frame, self)
        self.namesearch_page.show()
    def show_phonecheck_content(self):
        self.update_breadcrumb("Triumphoby / Phone Check")
        for btn in self.sidebar_buttons.values():
            btn.set_active(False)
        self.sidebar_buttons['phonecheck'].set_active(True)
        if not hasattr(self, 'phonecheck_page') or not self.phonecheck_page:
            self.phonecheck_page = PhoneCheckPage(self.content_frame, self)
        self.phonecheck_page.show()
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    def run(self):
        self.center_window()
        self.root.mainloop()
if __name__ == "__main__":
    app = TriumphOSINT()
    app.run()