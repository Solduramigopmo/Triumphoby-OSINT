import customtkinter as ctk
from config import COLORS
class CustomDropdown:
    _all_dropdowns = []
    def __init__(self, parent, values, default_value, command=None):
        self.parent = parent
        self.values = values
        self.current_value = default_value
        self.command = command
        self.is_open = False
        self.animation_running = False
        self.container = ctk.CTkFrame(parent, fg_color="transparent")
        self.button = ctk.CTkButton(
            self.container,
            text=f"{self.current_value} ▼",
            command=self.toggle,
            height=36,
            corner_radius=6,
            font=("Segoe UI", 11),
            fg_color=COLORS['surface_solid'],
            hover_color=COLORS['surface_light'],
            text_color=COLORS['text'],
            border_width=1,
            border_color=COLORS['border'],
            anchor="w"
        )
        self.button.pack(fill="x")
        self.dropdown_frame = None
        self.scrollable_frame = None
        CustomDropdown._all_dropdowns.append(self)
    def pack(self, **kwargs):
        self.container.pack(**kwargs)
    @classmethod
    def close_all(cls):
        for dropdown in cls._all_dropdowns:
            if dropdown.is_open:
                dropdown.close()
    def toggle(self):
        if self.is_open:
            self.close()
        else:
            CustomDropdown.close_all()
            self.open()
    def open(self):
        if self.dropdown_frame or self.animation_running:
            return
        self.animation_running = True
        self.button.update_idletasks()
        self.container.update_idletasks()
        root = self.parent
        while hasattr(root, 'master') and root.master:
            root = root.master
        x = self.button.winfo_rootx() - root.winfo_rootx()
        y = self.button.winfo_rooty() - root.winfo_rooty() + self.button.winfo_height() + 3
        width = self.button.winfo_width()
        item_height = 32
        padding = 5 + 5 + (len(self.values) - 1) * 2
        full_height = len(self.values) * item_height + padding
        max_height = 250
        self.target_height = min(full_height, max_height)
        needs_scroll = full_height > max_height
        self.dropdown_frame = ctk.CTkFrame(
            root,
            fg_color=COLORS['surface_solid'],
            corner_radius=6,
            border_width=1,
            border_color=COLORS['border'],
            width=width,
            height=0
        )
        self.dropdown_frame.place(x=x, y=y)
        self.dropdown_frame.pack_propagate(False)
        if needs_scroll:
            self.scrollable_frame = ctk.CTkScrollableFrame(
                self.dropdown_frame,
                fg_color="transparent",
                corner_radius=0,
                scrollbar_button_color=COLORS['accent'],
                scrollbar_button_hover_color=COLORS['accent_hover']
            )
            self.scrollable_frame.pack(fill="both", expand=True, padx=2, pady=2)
            parent_for_buttons = self.scrollable_frame
        else:
            parent_for_buttons = self.dropdown_frame
        for i, value in enumerate(self.values):
            pady_top = 5 if i == 0 else 2
            pady_bottom = 5 if i == len(self.values) - 1 else 2
            display_text = value if len(value) <= 50 else value[:47] + "..."
            btn = ctk.CTkButton(
                parent_for_buttons,
                text=display_text,
                command=lambda v=value: self.select(v),
                height=32,
                corner_radius=5,
                font=("Segoe UI", 11),
                fg_color="transparent",
                hover_color=COLORS['accent'],
                text_color=COLORS['text'],
                border_width=0,
                anchor="w"
            )
            btn.pack(fill="x", padx=5, pady=(pady_top, pady_bottom))
        self.button.configure(text=f"{self.current_value} ▲")
        self.is_open = True
        self.animate_slide_down()
    def animate_slide_down(self):
        duration = 250
        fps = 144
        delay = 1000 // fps
        steps = (duration * fps) // 1000
        def slide_step(step):
            if step <= steps and self.dropdown_frame:
                progress = step / steps
                eased_progress = 1 - (1 - progress) * (1 - progress)
                current_height = int(self.target_height * eased_progress)
                try:
                    self.dropdown_frame.configure(height=current_height)
                    self.dropdown_frame.update_idletasks()
                    if step < steps:
                        self.dropdown_frame.after(delay, lambda: slide_step(step + 1))
                    else:
                        self.dropdown_frame.configure(height=self.target_height)
                        self.dropdown_frame.update_idletasks()
                        self.animation_running = False
                except:
                    self.animation_running = False
            else:
                self.animation_running = False
        slide_step(1)
    def close(self):
        if not self.dropdown_frame or self.animation_running:
            return
        self.animation_running = True
        self.button.configure(text=f"{self.current_value} ▼")
        self.animate_slide_up()
    def animate_slide_up(self):
        duration = 200
        fps = 144
        delay = 1000 // fps
        steps = (duration * fps) // 1000
        if not hasattr(self, 'target_height'):
            self.destroy_dropdown()
            return
        def slide_step(step):
            if step <= steps and self.dropdown_frame:
                progress = step / steps
                eased_progress = progress * progress
                current_height = int(self.target_height * (1 - eased_progress))
                try:
                    self.dropdown_frame.configure(height=current_height)
                    self.dropdown_frame.update_idletasks()
                    if step < steps:
                        self.dropdown_frame.after(delay, lambda: slide_step(step + 1))
                    else:
                        self.destroy_dropdown()
                except:
                    self.destroy_dropdown()
            else:
                self.destroy_dropdown()
        slide_step(1)
    def destroy_dropdown(self):
        if self.dropdown_frame:
            try:
                self.dropdown_frame.update_idletasks()
                self.dropdown_frame.place_forget()
                self.dropdown_frame.destroy()
            except:
                pass
            finally:
                self.dropdown_frame = None
                self.scrollable_frame = None
        self.button.configure(text=f"{self.current_value} ▼")
        self.is_open = False
        self.animation_running = False
        try:
            root = self.parent
            while hasattr(root, 'master') and root.master:
                root = root.master
            root.update_idletasks()
        except:
            pass
    def select(self, value):
        self.current_value = value
        display_text = value if len(value) <= 40 else value[:37] + "..."
        self.button.configure(text=f"{display_text} ▼")
        self.close()
        if self.command:
            self.command(value)
    def get(self):
        return self.current_value
    def set(self, value):
        if value in self.values:
            self.current_value = value
            display_text = value if len(value) <= 40 else value[:37] + "..."
            self.button.configure(text=f"{display_text} ▼")
class GlowButton(ctk.CTkButton):
    def __init__(self, parent, text, command=None, style="primary", **kwargs):
        colors = {
            'primary': (COLORS['accent'], COLORS['accent_hover']),
            'success': (COLORS['success'], '#34d399'),
            'danger': (COLORS['danger'], '#f87171'),
        }
        fg_color, hover_color = colors.get(style, colors['primary'])
        super().__init__(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10),
            fg_color=fg_color,
            hover_color=hover_color,
            text_color="#ffffff",
            corner_radius=5,
            height=32,
            border_width=0,
            **kwargs
        )
class SidebarButton(ctk.CTkButton):
    def __init__(self, parent, text, command=None, **kwargs):
        self.default_color = COLORS['text_dim']
        self.hover_color_text = COLORS['text']
        self.active = False
        super().__init__(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10),
            fg_color="transparent",
            hover_color=COLORS['surface_light'],
            text_color=COLORS['text_dim'],
            anchor="w",
            corner_radius=5,
            height=28,
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )
    def set_active(self, active):
        self.active = active
        if active:
            self.configure(
                fg_color=COLORS['accent'],
                hover_color=COLORS['accent'],
                text_color="#ffffff",
                border_width=0
            )
        else:
            self.configure(
                fg_color="transparent",
                hover_color=COLORS['surface_light'],
                text_color=self.default_color,
                border_width=1,
                border_color=COLORS['border']
            )