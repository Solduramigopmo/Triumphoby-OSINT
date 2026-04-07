import customtkinter as ctk
import threading
import time
from config import COLORS, SEARCH_ENGINES, DORK_TEMPLATES
from ui.widgets import CustomDropdown, GlowButton
from core.search import SearchEngine
class BasePage:
    def __init__(self, parent, app=None):
        self.parent = parent
        self.app = app
        self.container = None
        self.rendered = False
    def render(self):
        raise NotImplementedError
    def show(self):
        for widget in self.parent.winfo_children():
            try:
                if self.container and widget == self.container:
                    continue
                widget.pack_forget()
            except:
                pass
        container_exists = False
        is_mapped = False
        if self.container is not None:
            try:
                self.container.winfo_exists()
                is_mapped = self.container.winfo_ismapped()
                container_exists = True
            except:
                container_exists = False
                self.container = None
                self.rendered = False
        if not container_exists or not self.rendered:
            self.render()
            return
        try:
            if not is_mapped:
                self.container.pack(fill="both", expand=True, padx=25, pady=25)
        except:
            self.rendered = False
            self.container = None
            self.show()
    def hide(self):
        if self.container:
            try:
                self.container.pack_forget()
            except:
                pass
class ComingSoonPage(BasePage):
    def __init__(self, parent, module_name):
        super().__init__(parent)
        self.module_name = module_name
    def render(self):
        if self.rendered:
            return
        for widget in self.parent.winfo_children():
            try:
                widget.pack_forget()
            except:
                pass
        self.container = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.container.place(relx=0.5, rely=0.5, anchor="center")
        title = ctk.CTkLabel(
            self.container,
            text=self.module_name,
            font=("Segoe UI", 24),
            text_color=COLORS['text']
        )
        title.pack(pady=(0, 8))
        subtitle = ctk.CTkLabel(
            self.container,
            text="Coming Soon",
            font=("Segoe UI", 12),
            text_color=COLORS['text_dim']
        )
        subtitle.pack()
        self.rendered = True
class SettingsPage(BasePage):
    def render(self):
        if self.rendered:
            print("[SETTINGS] Already rendered, skipping")
            return
        print("[SETTINGS] Rendering settings page...")
        for widget in self.parent.winfo_children():
            try:
                widget.pack_forget()
            except:
                pass
        self.container = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent",
            scrollbar_button_color=COLORS['accent'],
            scrollbar_button_hover_color=COLORS['accent_hover']
        )
        self.container.pack(fill="both", expand=True, padx=25, pady=25)
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(
            header,
            text="Settings",
            font=("Segoe UI", 22),
            text_color=COLORS['text']
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Configure application appearance",
            font=("Segoe UI", 11),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(3, 0))
        blur_panel = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        blur_panel.pack(fill="x", pady=(0, 15))
        blur_inner = ctk.CTkFrame(blur_panel, fg_color="transparent")
        blur_inner.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(
            blur_inner,
            text="Appearance",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(0, 15))
        blur_type_frame = ctk.CTkFrame(blur_inner, fg_color="transparent")
        blur_type_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            blur_type_frame,
            text="Blur Type",
            font=("Segoe UI", 11),
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(0, 8))
        self.blur_type_dropdown = CustomDropdown(
            blur_type_frame,
            values=["None", "Standard", "Acrylic"],
            default_value=self.app.settings['blur_type'],
            command=self.update_blur_type
        )
        self.blur_type_dropdown.pack(fill="x")
        intensity_frame = ctk.CTkFrame(blur_inner, fg_color="transparent")
        intensity_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            intensity_frame,
            text="Background Opacity",
            font=("Segoe UI", 11),
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(0, 8))
        self.opacity_slider = ctk.CTkSlider(
            intensity_frame,
            from_=0.7,
            to=1.0,
            number_of_steps=30,
            command=self.update_opacity,
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover'],
            progress_color=COLORS['accent'],
            fg_color=COLORS['bg']
        )
        self.opacity_slider.set(self.app.settings.get('bg_opacity', 0.95))
        self.opacity_slider.pack(fill="x", pady=(0, 5))
        self.opacity_label = ctk.CTkLabel(
            intensity_frame,
            text=f"{int(self.app.settings.get('bg_opacity', 0.95) * 100)}%",
            font=("Segoe UI", 10),
            text_color=COLORS['text_dim']
        )
        self.opacity_label.pack(anchor="w")
        apply_frame = ctk.CTkFrame(blur_inner, fg_color="transparent")
        apply_frame.pack(fill="x", pady=(10, 0))
        GlowButton(
            apply_frame,
            text="Apply Changes",
            command=self.apply_blur_settings,
            style="primary",
            width=150
        ).pack(side="left")
        ctk.CTkLabel(
            apply_frame,
            text="Changes apply immediately",
            font=("Segoe UI", 9),
            text_color=COLORS['text_darker']
        ).pack(side="left", padx=(15, 0))
        api_panel = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        api_panel.pack(fill="x", pady=(0, 15))
        api_inner = ctk.CTkFrame(api_panel, fg_color="transparent")
        api_inner.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(
            api_inner,
            text="API Keys (Phone Check) v2.0",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            api_inner,
            text="Add API keys for better phone intelligence results",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(0, 15))
        smsc_frame = ctk.CTkFrame(api_inner, fg_color="transparent")
        smsc_frame.pack(fill="x", pady=(0, 10))
        smsc_header = ctk.CTkFrame(smsc_frame, fg_color="transparent")
        smsc_header.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(
            smsc_header,
            text="SMSC.ru (HLR Lookup)",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS['text']
        ).pack(side="left")
        ctk.CTkLabel(
            smsc_header,
            text="Get: https://smsc.ru/ | From 100 RUB",
            font=("Segoe UI", 8),
            text_color=COLORS['text_darker']
        ).pack(side="left", padx=(10, 0))
        smsc_row = ctk.CTkFrame(smsc_frame, fg_color="transparent")
        smsc_row.pack(fill="x")
        smsc_login_frame = ctk.CTkFrame(smsc_row, fg_color="transparent")
        smsc_login_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(
            smsc_login_frame,
            text="Login",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(0, 4))
        self.smsc_login_entry = ctk.CTkEntry(
            smsc_login_frame,
            height=30,
            font=("Segoe UI", 10),
            border_width=1,
            fg_color=COLORS['surface_solid'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=8,
            placeholder_text="your_login",
            placeholder_text_color=COLORS['text_darker']
        )
        self.smsc_login_entry.insert(0, self.app.settings.get('smsc_login', ''))
        self.smsc_login_entry.pack(fill="x")
        smsc_psw_frame = ctk.CTkFrame(smsc_row, fg_color="transparent")
        smsc_psw_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            smsc_psw_frame,
            text="Password",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(0, 4))
        self.smsc_psw_entry = ctk.CTkEntry(
            smsc_psw_frame,
            height=30,
            font=("Segoe UI", 10),
            border_width=1,
            fg_color=COLORS['surface_solid'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=8,
            placeholder_text="your_password",
            placeholder_text_color=COLORS['text_darker'],
            show="*"
        )
        self.smsc_psw_entry.insert(0, self.app.settings.get('smsc_password', ''))
        self.smsc_psw_entry.pack(fill="x")
        print("[SETTINGS] SMSC.ru section created")
        numverify_frame = ctk.CTkFrame(api_inner, fg_color="transparent")
        numverify_frame.pack(fill="x", pady=(0, 10))
        numverify_header = ctk.CTkFrame(numverify_frame, fg_color="transparent")
        numverify_header.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(
            numverify_header,
            text="Numverify API",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS['text']
        ).pack(side="left")
        ctk.CTkLabel(
            numverify_header,
            text="Get: https://numverify.com/ | 100 free/month",
            font=("Segoe UI", 8),
            text_color=COLORS['text_darker']
        ).pack(side="left", padx=(10, 0))
        ctk.CTkLabel(
            numverify_frame,
            text="API Key",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(0, 4))
        self.numverify_entry = ctk.CTkEntry(
            numverify_frame,
            height=30,
            font=("Segoe UI", 10),
            border_width=1,
            fg_color=COLORS['surface_solid'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=8,
            placeholder_text="your_api_key",
            placeholder_text_color=COLORS['text_darker']
        )
        self.numverify_entry.insert(0, self.app.settings.get('numverify_api_key', ''))
        self.numverify_entry.pack(fill="x")
        print("[SETTINGS] Numverify section created")
        telegram_frame = ctk.CTkFrame(api_inner, fg_color="transparent")
        telegram_frame.pack(fill="x", pady=(0, 10))
        telegram_header = ctk.CTkFrame(telegram_frame, fg_color="transparent")
        telegram_header.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(
            telegram_header,
            text="Telegram API",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS['text']
        ).pack(side="left")
        ctk.CTkLabel(
            telegram_header,
            text="Get: https://my.telegram.org/apps | Free",
            font=("Segoe UI", 8),
            text_color=COLORS['text_darker']
        ).pack(side="left", padx=(10, 0))
        tg_row1 = ctk.CTkFrame(telegram_frame, fg_color="transparent")
        tg_row1.pack(fill="x", pady=(0, 5))
        tg_id_frame = ctk.CTkFrame(tg_row1, fg_color="transparent")
        tg_id_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(
            tg_id_frame,
            text="API ID",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(0, 4))
        self.telegram_id_entry = ctk.CTkEntry(
            tg_id_frame,
            height=30,
            font=("Segoe UI", 10),
            border_width=1,
            fg_color=COLORS['surface_solid'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=8,
            placeholder_text="12345678",
            placeholder_text_color=COLORS['text_darker']
        )
        self.telegram_id_entry.insert(0, self.app.settings.get('telegram_api_id', ''))
        self.telegram_id_entry.pack(fill="x")
        tg_hash_frame = ctk.CTkFrame(tg_row1, fg_color="transparent")
        tg_hash_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            tg_hash_frame,
            text="API Hash",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(0, 4))
        self.telegram_hash_entry = ctk.CTkEntry(
            tg_hash_frame,
            height=30,
            font=("Segoe UI", 10),
            border_width=1,
            fg_color=COLORS['surface_solid'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=8,
            placeholder_text="abcdef1234567890",
            placeholder_text_color=COLORS['text_darker']
        )
        self.telegram_hash_entry.insert(0, self.app.settings.get('telegram_api_hash', ''))
        self.telegram_hash_entry.pack(fill="x")
        print("[SETTINGS] Telegram section created")
        save_frame = ctk.CTkFrame(api_inner, fg_color="transparent")
        save_frame.pack(fill="x", pady=(10, 0))
        GlowButton(
            save_frame,
            text="Save API Keys",
            command=self.save_api_keys,
            style="success",
            width=150
        ).pack(side="left")
        ctk.CTkLabel(
            save_frame,
            text="Keys are saved locally and never shared",
            font=("Segoe UI", 9),
            text_color=COLORS['text_darker']
        ).pack(side="left", padx=(15, 0))
        print("[SETTINGS] Save button created")
        print("[SETTINGS] All API sections completed!")
        self.rendered = True
    def save_api_keys(self):
        self.app.settings['smsc_login'] = self.smsc_login_entry.get().strip()
        self.app.settings['smsc_password'] = self.smsc_psw_entry.get().strip()
        self.app.settings['numverify_api_key'] = self.numverify_entry.get().strip()
        self.app.settings['telegram_api_id'] = self.telegram_id_entry.get().strip()
        self.app.settings['telegram_api_hash'] = self.telegram_hash_entry.get().strip()
        self.app.save_settings()
        print("[SETTINGS] API keys saved successfully")
    def update_opacity(self, value):
        opacity = float(value)
        self.opacity_label.configure(text=f"{int(opacity * 100)}%")
        self.app.settings['bg_opacity'] = opacity
        self.app.save_settings()
        try:
            self.app.root.attributes('-alpha', opacity)
        except:
            pass
    def update_blur_type(self, choice):
        self.app.settings['blur_type'] = choice
        self.app.save_settings()
        self.apply_blur_settings()
    def update_transparency(self, value):
        try:
            opacity = float(value)
            self.app.root.attributes('-alpha', opacity)
            self.app.settings['bg_opacity'] = opacity
            self.app.save_settings()
        except:
            pass
    def apply_blur_settings(self):
        self.app.apply_dark_title_bar()
class DorkingPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.search_engine = None
        self.searching = False
    def toggle_proxy_fields(self):
        enabled = self.proxy_enabled_var.get()
        state = "normal" if enabled else "disabled"
        self.proxy_entry.configure(state=state)
    def get_search_engine(self):
        try:
            proxy_url = self.proxy_entry.get().strip()
            settings = {
                'max_results': int(self.max_results_entry.get() or 20),
                'timeout': int(self.timeout_entry.get() or 15),
                'delay_between_requests': float(self.delay_entry.get() or 2),
                'user_agent': self.user_agent_entry.get() or self.app.settings.get('user_agent', ''),
                'proxy_enabled': self.proxy_enabled_var.get(),
                'proxy_http': proxy_url,
                'proxy_https': proxy_url
            }
            return SearchEngine(settings)
        except Exception as e:
            print(f"[ERROR] Failed to create SearchEngine: {e}")
            return SearchEngine(self.app.settings)
    def render(self):
        if self.rendered:
            return
        self.container = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent",
            scrollbar_button_color=COLORS['accent'],
            scrollbar_button_hover_color=COLORS['accent_hover']
        )
        self.container.pack(fill="both", expand=True, padx=25, pady=25)
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(
            header,
            text="Dorking",
            font=("Segoe UI", 22),
            text_color=COLORS['text']
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Advanced search queries for OSINT",
            font=("Segoe UI", 11),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(3, 0))
        settings_panel = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['surface_solid'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border']
        )
        settings_panel.pack(fill="x", pady=(0, 15))
        settings_inner = ctk.CTkFrame(settings_panel, fg_color="transparent")
        settings_inner.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(
            settings_inner,
            text="Target",
            font=("Segoe UI", 11),
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(0, 6))
        self.keyword_entry = ctk.CTkEntry(
            settings_inner,
            height=36,
            font=("Segoe UI", 11),
            border_width=1,
            fg_color=COLORS['bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=10,
            placeholder_text='example.com'
        )
        self.keyword_entry.pack(fill="x", pady=(0, 15))
        row1 = ctk.CTkFrame(settings_inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 15))
        engine_frame = ctk.CTkFrame(row1, fg_color="transparent")
        engine_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(
            engine_frame,
            text="Engine",
            font=("Segoe UI", 11),
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(0, 6))
        self.engine_dropdown = CustomDropdown(
            engine_frame,
            values=list(SEARCH_ENGINES.keys()),
            default_value="DuckDuckGo"
        )
        self.engine_dropdown.pack(fill="x")
        template_frame = ctk.CTkFrame(row1, fg_color="transparent")
        template_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            template_frame,
            text="Template",
            font=("Segoe UI", 11),
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(0, 6))
        self.template_dropdown = CustomDropdown(
            template_frame,
            values=DORK_TEMPLATES,
            default_value=DORK_TEMPLATES[0]
        )
        self.template_dropdown.pack(fill="x")
        actions_frame = ctk.CTkFrame(settings_inner, fg_color="transparent")
        actions_frame.pack(fill="x")
        GlowButton(
            actions_frame,
            text="Search",
            command=self.start_search,
            style="primary",
            width=60
        ).pack(side="left", padx=(0, 6))
        GlowButton(
            actions_frame,
            text="Search All",
            command=self.search_all_templates,
            style="success",
            width=70
        ).pack(side="left", padx=(0, 6))
        self.stop_btn = GlowButton(
            actions_frame,
            text="Stop",
            command=self.stop_search,
            style="danger",
            width=50
        )
        self.stop_btn.pack(side="left")
        self.stop_btn.configure(state="disabled")
        advanced_panel = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['surface_solid'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border']
        )
        advanced_panel.pack(fill="x", pady=(0, 15))
        advanced_inner = ctk.CTkFrame(advanced_panel, fg_color="transparent")
        advanced_inner.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(
            advanced_inner,
            text="Advanced Settings",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(0, 12))
        row_params = ctk.CTkFrame(advanced_inner, fg_color="transparent")
        row_params.pack(fill="x", pady=(0, 12))
        max_frame = ctk.CTkFrame(row_params, fg_color="transparent")
        max_frame.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(
            max_frame,
            text="Max Results",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(0, 4))
        self.max_results_entry = ctk.CTkEntry(
            max_frame,
            height=30,
            font=("Segoe UI", 10),
            border_width=1,
            fg_color=COLORS['bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=8
        )
        self.max_results_entry.insert(0, str(self.app.settings.get('max_results', 20)))
        self.max_results_entry.pack(fill="x")
        timeout_frame = ctk.CTkFrame(row_params, fg_color="transparent")
        timeout_frame.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(
            timeout_frame,
            text="Timeout (sec)",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(0, 4))
        self.timeout_entry = ctk.CTkEntry(
            timeout_frame,
            height=30,
            font=("Segoe UI", 10),
            border_width=1,
            fg_color=COLORS['bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=8
        )
        self.timeout_entry.insert(0, str(self.app.settings.get('timeout', 15)))
        self.timeout_entry.pack(fill="x")
        delay_frame = ctk.CTkFrame(row_params, fg_color="transparent")
        delay_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            delay_frame,
            text="Delay (sec)",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(0, 4))
        self.delay_entry = ctk.CTkEntry(
            delay_frame,
            height=30,
            font=("Segoe UI", 10),
            border_width=1,
            fg_color=COLORS['bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=8
        )
        self.delay_entry.insert(0, str(self.app.settings.get('delay_between_requests', 2)))
        self.delay_entry.pack(fill="x")
        ua_frame = ctk.CTkFrame(advanced_inner, fg_color="transparent")
        ua_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            ua_frame,
            text="User Agent",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(0, 4))
        self.user_agent_entry = ctk.CTkEntry(
            ua_frame,
            height=30,
            font=("Segoe UI", 9),
            border_width=1,
            fg_color=COLORS['bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=8
        )
        self.user_agent_entry.insert(0, self.app.settings.get('user_agent', ''))
        self.user_agent_entry.pack(fill="x")
        self.proxy_enabled_var = ctk.BooleanVar(value=self.app.settings.get('proxy_enabled', False))
        ctk.CTkCheckBox(
            advanced_inner,
            text="Enable Proxy",
            variable=self.proxy_enabled_var,
            font=("Segoe UI", 10),
            text_color=COLORS['text'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            border_color=COLORS['border'],
            command=self.toggle_proxy_fields
        ).pack(anchor="w", pady=(0, 8))
        proxy_frame = ctk.CTkFrame(advanced_inner, fg_color="transparent")
        proxy_frame.pack(fill="x")
        ctk.CTkLabel(
            proxy_frame,
            text="Proxy (http://ip:port, https://ip:port, socks5://ip:port, socks5://user:pass@ip:port)",
            font=("Segoe UI", 9),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(0, 4))
        self.proxy_entry = ctk.CTkEntry(
            proxy_frame,
            height=30,
            font=("Segoe UI", 9),
            border_width=1,
            fg_color=COLORS['bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=8,
            placeholder_text="http://127.0.0.1:8080 or socks5://user:pass@127.0.0.1:1080"
        )
        saved_proxy = self.app.settings.get('proxy_http', '') or self.app.settings.get('proxy_https', '')
        self.proxy_entry.insert(0, saved_proxy)
        self.proxy_entry.pack(fill="x")
        self.toggle_proxy_fields()
        progress_frame = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['surface_solid'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border']
        )
        progress_frame.pack(fill="x", pady=(0, 15))
        progress_inner = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_inner.pack(fill="x", padx=20, pady=15)
        self.status_label = ctk.CTkLabel(
            progress_inner,
            text="Ready",
            font=("Segoe UI", 10),
            text_color=COLORS['text_dim']
        )
        self.status_label.pack(anchor="w", pady=(0, 8))
        self.progress_bar = ctk.CTkProgressBar(
            progress_inner,
            height=6,
            corner_radius=10,
            fg_color=COLORS['bg'],
            progress_color=COLORS['accent']
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        results_header = ctk.CTkFrame(self.container, fg_color="transparent")
        results_header.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(
            results_header,
            text="Results",
            font=("Segoe UI", 13),
            text_color=COLORS['text']
        ).pack(side="left")
        ctk.CTkButton(
            results_header,
            text="Clear",
            command=self.clear_results,
            width=80,
            height=30,
            fg_color="transparent",
            hover_color=COLORS['surface_solid'],
            text_color=COLORS['text_dim'],
            border_width=1,
            border_color=COLORS['border'],
            corner_radius=10,
            font=("Segoe UI", 10)
        ).pack(side="right")
        results_frame = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['surface_solid'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border']
        )
        results_frame.pack(fill="both", expand=True)
        self.results_text = ctk.CTkTextbox(
            results_frame,
            fg_color=COLORS['bg'],
            text_color=COLORS['text'],
            font=("Segoe UI", 10),
            corner_radius=10,
            wrap="word",
            border_width=0
        )
        self.results_text.pack(fill="both", expand=True, padx=2, pady=2)
        self.rendered = True
    def start_search(self):
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            return
        template = self.template_dropdown.get()
        dork_query = template.replace("{keyword}", keyword)
        engine = self.engine_dropdown.get()
        self.searching = True
        self.stop_btn.configure(state="normal")
        self.update_status("Searching...", 0.3)
        thread = threading.Thread(target=self._search_thread, args=(dork_query, engine))
        thread.daemon = True
        thread.start()
    def search_all_templates(self):
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            return
        self.searching = True
        self.stop_btn.configure(state="normal")
        self.clear_results()
        thread = threading.Thread(target=self._search_all_thread, args=(keyword,))
        thread.daemon = True
        thread.start()
    def _search_thread(self, query, engine):
        try:
            print(f"[THREAD] Starting search: {query} on {engine}")
            search_engine = self.get_search_engine()
            results = search_engine.search(query, engine)
            print(f"[THREAD] Got {len(results)} results")
            if results:
                print(f"[THREAD] First result: {results[0]}")
                print(f"[THREAD] Calling display_results with {len(results)} items")
            else:
                print(f"[THREAD] No results to display")
            results_copy = list(results)
            self.app.root.after(0, lambda r=results_copy: self.display_results(r))
            self.app.root.after(0, lambda c=len(results): self.update_status(f"Found {c} results", 1.0))
        except Exception as e:
            print(f"[THREAD] Error: {e}")
            import traceback
            traceback.print_exc()
            error_msg = str(e)
            self.app.root.after(0, lambda msg=error_msg: self.update_status(f"Error: {msg}", 0.0))
        finally:
            self.searching = False
            self.app.root.after(0, lambda: self.stop_btn.configure(state="disabled"))
    def _search_all_thread(self, keyword):
        engine = self.engine_dropdown.get()
        total = len(DORK_TEMPLATES)
        delay = self.app.settings.get('delay_between_requests', 2)
        for i, template in enumerate(DORK_TEMPLATES):
            if not self.searching:
                break
            dork_query = template.replace("{keyword}", keyword)
            progress = (i + 1) / total
            self.app.root.after(0, lambda p=progress, idx=i+1, t=total:
                self.update_status(f"Searching template {idx}/{t}", p))
            try:
                search_engine = self.get_search_engine()
                results = search_engine.search(dork_query, engine)
                self.app.root.after(0, lambda tpl=template, res=results: (
                    self.append_result(f"\n{'='*60}"),
                    self.append_result(f"Template: {tpl}"),
                    self.append_result(f"{'='*60}\n"),
                    self.display_results(res)
                ))
                time.sleep(delay)
            except Exception as e:
                self.app.root.after(0, lambda err=e, tpl=template:
                    self.append_result(f"Error with {tpl}: {err}\n"))
        self.app.root.after(0, lambda: self.update_status("All templates searched", 1.0))
        self.searching = False
        self.app.root.after(0, lambda: self.stop_btn.configure(state="disabled"))
    def display_results(self, results):
        print(f"[DISPLAY] Called with {len(results) if results else 0} results")
        if not results:
            self.append_result("No results found.")
            return
        print(f"[DISPLAY] Displaying {len(results)} results")
        self.append_result(f"Found {len(results)} results:\n")
        self.append_result("=" * 80)
        for i, result in enumerate(results, 1):
            print(f"[DISPLAY] Result {i}: {result.get('title', 'NO TITLE')[:50]}")
            self.append_result(f"\n[{i}] {result.get('title', 'No title')}")
            self.append_result(f"    URL: {result.get('url', 'No URL')}")
            if result.get('snippet'):
                snippet = result['snippet']
                self.append_result(f"    Description: {snippet}")
            self.append_result("")
        self.append_result("=" * 80)
        print(f"[DISPLAY] Finished displaying results")
    def append_result(self, text):
        self.results_text.insert("end", text + "\n")
        self.results_text.see("end")
    def update_status(self, message, progress):
        self.status_label.configure(text=message)
        self.progress_bar.set(progress)
    def stop_search(self):
        self.searching = False
        self.update_status("Stopped", 0.0)
        self.stop_btn.configure(state="disabled")
    def clear_results(self):
        self.results_text.delete("1.0", "end")
        self.update_status("Ready", 0.0)
class NameSearchPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.searching = False
        self.result_cards = []
    def render(self):
        if self.rendered:
            return
        self.container = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent",
            scrollbar_button_color=COLORS['accent'],
            scrollbar_button_hover_color=COLORS['accent_hover']
        )
        self.container.pack(fill="both", expand=True, padx=25, pady=25)
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(
            header,
            text="Name Search",
            font=("Segoe UI", 22),
            text_color=COLORS['text']
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Check username availability across 500+ services",
            font=("Segoe UI", 11),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(3, 0))
        search_panel = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        search_panel.pack(fill="x", pady=(0, 15))
        search_inner = ctk.CTkFrame(search_panel, fg_color="transparent")
        search_inner.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(
            search_inner,
            text="Username",
            font=("Segoe UI", 11),
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(0, 6))
        self.username_entry = ctk.CTkEntry(
            search_inner,
            height=36,
            font=("Segoe UI", 11),
            border_width=1,
            fg_color=COLORS['bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=6,
            placeholder_text='username'
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        actions_frame = ctk.CTkFrame(search_inner, fg_color="transparent")
        actions_frame.pack(fill="x")
        GlowButton(
            actions_frame,
            text="Search",
            command=self.start_search,
            style="primary",
            width=60
        ).pack(side="left", padx=(0, 6))
        self.stop_btn = GlowButton(
            actions_frame,
            text="Stop",
            command=self.stop_search,
            style="danger",
            width=50
        )
        self.stop_btn.pack(side="left")
        self.stop_btn.configure(state="disabled")
        progress_frame = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        progress_frame.pack(fill="x", pady=(0, 15))
        progress_inner = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_inner.pack(fill="x", padx=20, pady=15)
        self.status_label = ctk.CTkLabel(
            progress_inner,
            text="Ready",
            font=("Segoe UI", 10),
            text_color=COLORS['text_dim']
        )
        self.status_label.pack(anchor="w", pady=(0, 8))
        self.progress_bar = ctk.CTkProgressBar(
            progress_inner,
            height=6,
            corner_radius=6,
            fg_color=COLORS['bg'],
            progress_color=COLORS['accent']
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        results_header = ctk.CTkFrame(self.container, fg_color="transparent")
        results_header.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(
            results_header,
            text="Results",
            font=("Segoe UI", 13),
            text_color=COLORS['text']
        ).pack(side="left")
        ctk.CTkButton(
            results_header,
            text="Clear",
            command=self.clear_results,
            width=80,
            height=30,
            fg_color="transparent",
            hover_color=COLORS['surface_solid'],
            text_color=COLORS['text_dim'],
            border_width=1,
            border_color=COLORS['border'],
            corner_radius=6,
            font=("Segoe UI", 10)
        ).pack(side="right")
        results_frame = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        results_frame.pack(fill="both", expand=True)
        self.results_container = ctk.CTkScrollableFrame(
            results_frame,
            fg_color=COLORS['bg'],
            corner_radius=6,
            scrollbar_button_color=COLORS['accent'],
            scrollbar_button_hover_color=COLORS['accent_hover']
        )
        self.results_container.pack(fill="both", expand=True, padx=2, pady=2)
        self.rendered = True
    def start_search(self):
        username = self.username_entry.get().strip()
        if not username:
            return
        self.searching = True
        self.stop_btn.configure(state="normal")
        self.clear_results()
        self.update_status("Searching...", 0.1)
        thread = threading.Thread(target=self._search_thread, args=(username,))
        thread.daemon = True
        thread.start()
    def _search_thread(self, username):
        try:
            from core.username_checker import UsernameChecker
            checker = UsernameChecker()
            def progress_callback(index, total, result):
                progress = (index + 1) / total
                self.app.root.after(0, lambda p=progress, n=result['name']:
                    self.update_status(f"Checking {n}...", p))
                self.app.root.after(0, lambda idx=index, r=result:
                    self.add_result_card(idx, r['name'], r['url'], r['found']))
            def should_stop():
                return not self.searching
            checker.check_all(username, callback=progress_callback, stop_flag=should_stop)
            self.app.root.after(0, lambda: self.update_status("Search completed", 1.0))
        except Exception as e:
            print(f"[ERROR] Name search failed: {e}")
            import traceback
            traceback.print_exc()
            self.app.root.after(0, lambda: self.update_status(f"Error: {str(e)}", 0.0))
        finally:
            self.searching = False
            self.app.root.after(0, lambda: self.stop_btn.configure(state="disabled"))
    def add_result_card(self, index, service_name, url, found):
        bg_color = COLORS['bg'] if index % 2 == 0 else COLORS['surface_solid']
        if found:
            status_text = "[+]"
            status_color = COLORS['success']
        else:
            status_text = "[-]"
            status_color = COLORS['danger']
        card = ctk.CTkFrame(
            self.results_container,
            fg_color=bg_color,
            corner_radius=5,
            height=32
        )
        card.pack(fill="x", padx=5, pady=1)
        card.pack_propagate(False)
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=5)
        status_label = ctk.CTkLabel(
            content,
            text=status_text,
            font=("Segoe UI", 10, "bold"),
            text_color=status_color,
            width=25
        )
        status_label.pack(side="left", padx=(0, 8))
        name_label = ctk.CTkLabel(
            content,
            text=service_name,
            font=("Segoe UI", 10),
            text_color=COLORS['text'],
            anchor="w",
            width=100
        )
        name_label.pack(side="left", padx=(0, 8))
        if found:
            link_button = ctk.CTkButton(
                content,
                text=url,
                command=lambda u=url: self.open_url(u),
                font=("Segoe UI", 9),
                fg_color="transparent",
                hover_color=COLORS['surface_light'],
                text_color=COLORS['accent'],
                anchor="w",
                corner_radius=3,
                height=20,
                border_width=0
            )
            link_button.pack(side="left", fill="x", expand=True)
        else:
            url_label = ctk.CTkLabel(
                content,
                text=url,
                font=("Segoe UI", 9),
                text_color=COLORS['text_darker'],
                anchor="w"
            )
            url_label.pack(side="left", fill="x", expand=True)
        self.result_cards.append(card)
    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)
    def append_result(self, text):
        pass
    def update_status(self, message, progress):
        self.status_label.configure(text=message)
        self.progress_bar.set(progress)
    def stop_search(self):
        self.searching = False
        self.update_status("Stopped", 0.0)
        self.stop_btn.configure(state="disabled")
    def clear_results(self):
        for card in self.result_cards:
            card.destroy()
        self.result_cards.clear()
        self.update_status("Ready", 0.0)
class PhoneCheckPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.checking = False
        self.result_data = None
    def render(self):
        if self.rendered:
            return
        self.container = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent",
            scrollbar_button_color=COLORS['accent'],
            scrollbar_button_hover_color=COLORS['accent_hover']
        )
        self.container.pack(fill="both", expand=True, padx=25, pady=25)
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(
            header,
            text="Phone Check",
            font=("Segoe UI", 22),
            text_color=COLORS['text']
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Phone number intelligence: validation, carrier, HLR lookup, online status",
            font=("Segoe UI", 11),
            text_color=COLORS['text_dim']
        ).pack(anchor="w", pady=(3, 0))
        input_panel = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        input_panel.pack(fill="x", pady=(0, 15))
        input_inner = ctk.CTkFrame(input_panel, fg_color="transparent")
        input_inner.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(
            input_inner,
            text="Phone Number",
            font=("Segoe UI", 11),
            text_color=COLORS['text']
        ).pack(anchor="w", pady=(0, 6))
        phone_frame = ctk.CTkFrame(input_inner, fg_color="transparent")
        phone_frame.pack(fill="x", pady=(0, 15))
        self.phone_entry = ctk.CTkEntry(
            phone_frame,
            height=36,
            font=("Segoe UI", 11),
            border_width=1,
            fg_color=COLORS['bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=6,
            placeholder_text='+1234567890 or 1234567890'
        )
        self.phone_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.region_entry = ctk.CTkEntry(
            phone_frame,
            height=36,
            width=80,
            font=("Segoe UI", 11),
            border_width=1,
            fg_color=COLORS['bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            corner_radius=6,
            placeholder_text='US'
        )
        self.region_entry.pack(side="left")
        actions_frame = ctk.CTkFrame(input_inner, fg_color="transparent")
        actions_frame.pack(fill="x")
        GlowButton(
            actions_frame,
            text="Check",
            command=self.start_check,
            style="primary",
            width=60
        ).pack(side="left", padx=(0, 6))
        self.stop_btn = GlowButton(
            actions_frame,
            text="Stop",
            command=self.stop_check,
            style="danger",
            width=50
        )
        self.stop_btn.pack(side="left")
        self.stop_btn.configure(state="disabled")
        progress_frame = ctk.CTkFrame(
            self.container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        progress_frame.pack(fill="x", pady=(0, 15))
        progress_inner = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_inner.pack(fill="x", padx=20, pady=15)
        self.status_label = ctk.CTkLabel(
            progress_inner,
            text="Ready",
            font=("Segoe UI", 10),
            text_color=COLORS['text_dim']
        )
        self.status_label.pack(anchor="w", pady=(0, 8))
        self.progress_bar = ctk.CTkProgressBar(
            progress_inner,
            height=6,
            corner_radius=6,
            fg_color=COLORS['bg'],
            progress_color=COLORS['accent']
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        results_header = ctk.CTkFrame(self.container, fg_color="transparent")
        results_header.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(
            results_header,
            text="Results",
            font=("Segoe UI", 13),
            text_color=COLORS['text']
        ).pack(side="left")
        ctk.CTkButton(
            results_header,
            text="Clear",
            command=self.clear_results,
            width=80,
            height=30,
            fg_color="transparent",
            hover_color=COLORS['surface_solid'],
            text_color=COLORS['text_dim'],
            border_width=1,
            border_color=COLORS['border'],
            corner_radius=6,
            font=("Segoe UI", 10)
        ).pack(side="right")
        self.results_container = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        self.results_container.pack(fill="both", expand=True)
        self.rendered = True
    def start_check(self):
        phone = self.phone_entry.get().strip()
        if not phone:
            return
        region = self.region_entry.get().strip() or None
        self.checking = True
        self.stop_btn.configure(state="normal")
        self.clear_results()
        self.update_status("Checking phone number...", 0.2)
        thread = threading.Thread(target=self._check_thread, args=(phone, region))
        thread.daemon = True
        thread.start()
    def _check_thread(self, phone, region):
        try:
            import asyncio
            from core.phone_checker import PhoneChecker
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            async def run_check():
                async with PhoneChecker(self.app.settings) as checker:
                    self.app.root.after(0, lambda: self.update_status("Running full check...", 0.4))
                    result = await checker.full_check(phone, region)
                    return result
            result = loop.run_until_complete(run_check())
            loop.close()
            self.result_data = result
            self.app.root.after(0, lambda r=result: self.display_results(r))
            self.app.root.after(0, lambda: self.update_status("Check completed", 1.0))
        except Exception as e:
            print(f"[ERROR] Phone check failed: {e}")
            import traceback
            traceback.print_exc()
            self.app.root.after(0, lambda: self.update_status(f"Error: {str(e)}", 0.0))
            self.app.root.after(0, lambda err=str(e): self.show_error(err))
        finally:
            self.checking = False
            self.app.root.after(0, lambda: self.stop_btn.configure(state="disabled"))
    def show_error(self, error_msg):
        error_card = ctk.CTkFrame(
            self.results_container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['danger']
        )
        error_card.pack(fill="x", pady=5)
        error_inner = ctk.CTkFrame(error_card, fg_color="transparent")
        error_inner.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(
            error_inner,
            text=f"❌ Error: {error_msg}",
            font=("Segoe UI", 11),
            text_color=COLORS['danger'],
            anchor="w"
        ).pack(fill="x")
    def display_results(self, result):
        if 'error' in result:
            self.show_error(result['error'])
            return
        if 'basic' in result:
            self.create_main_info_card(result['basic'])
        if 'sources' in result:
            sources = result['sources']
            if 'hlr' in sources:
                self.create_source_card('HLR Lookup (SMSC.ru)', sources['hlr'])
            if 'truecaller' in sources:
                self.create_source_card('Truecaller', sources['truecaller'])
            if 'getcontact' in sources:
                self.create_source_card('GetContact', sources['getcontact'])
            if 'eyecon' in sources:
                self.create_source_card('Eyecon', sources['eyecon'])
            if 'social_media' in sources:
                self.create_social_media_card(sources['social_media'])
            if 'google' in sources:
                self.create_google_card(sources['google'])
            if 'online_status' in sources:
                self.create_messenger_card(sources['online_status'], result['basic'].get('e164', ''))
        else:
            if 'hlr' in result:
                self.create_source_card('HLR Lookup', result['hlr'])
            if 'online_status' in result:
                self.create_messenger_card(result['online_status'], result['basic'].get('e164', ''))
    def create_main_info_card(self, basic):
        card = ctk.CTkFrame(
            self.results_container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        card.pack(fill="x", pady=5)
        card_inner = ctk.CTkFrame(card, fg_color="transparent")
        card_inner.pack(fill="x", padx=20, pady=20)
        header_frame = ctk.CTkFrame(card_inner, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        flag_label = ctk.CTkLabel(
            header_frame,
            text=basic.get('country_flag', '🌍'),
            font=("Segoe UI", 32),
            text_color=COLORS['text']
        )
        flag_label.pack(side="left", padx=(0, 15))
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            info_frame,
            text=basic.get('international', 'N/A'),
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS['text'],
            anchor="w"
        ).pack(anchor="w")
        location_text = basic.get('location', 'Unknown')
        if location_text:
            ctk.CTkLabel(
                info_frame,
                text=location_text,
                font=("Segoe UI", 11),
                text_color=COLORS['text_dim'],
                anchor="w"
            ).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(
            info_frame,
            text="Format validation only. Check HLR for real status.",
            font=("Segoe UI", 8),
            text_color=COLORS['text_darker'],
            anchor="w"
        ).pack(anchor="w", pady=(2, 0))
        status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_frame.pack(side="right")
        valid = basic.get('valid', False)
        status_color = COLORS['success'] if valid else COLORS['danger']
        status_text = "Valid Format" if valid else "Invalid Format"
        status_badge = ctk.CTkFrame(
            status_frame,
            fg_color=status_color,
            corner_radius=12
        )
        status_badge.pack()
        ctk.CTkLabel(
            status_badge,
            text=status_text,
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS['text']
        ).pack(padx=12, pady=6)
        separator = ctk.CTkFrame(card_inner, height=1, fg_color=COLORS['border'])
        separator.pack(fill="x", pady=(0, 15))
        details_data = [
            ("Carrier", basic.get('carrier', 'Unknown')),
            ("Type", basic.get('number_type', 'Unknown')),
            ("Country Code", f"+{basic.get('country_code', 'N/A')}"),
            ("National Format", basic.get('national', 'N/A')),
            ("E.164 Format", basic.get('e164', 'N/A')),
            ("Timezone", ', '.join(basic.get('timezones', ['Unknown'])))
        ]
        for index, (label, value) in enumerate(details_data):
            self.add_detail_row_alternating(card_inner, label, value, index)
    def create_source_card(self, title: str, data: dict):
        card = ctk.CTkFrame(
            self.results_container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        card.pack(fill="x", pady=5)
        card_inner = ctk.CTkFrame(card, fg_color="transparent")
        card_inner.pack(fill="x", padx=20, pady=15)
        header_frame = ctk.CTkFrame(card_inner, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            header_frame,
            text=title,
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS['text'],
            anchor="w"
        ).pack(side="left")
        if 'status' in data:
            status = data['status']
            if status == 'Available' or status == 'available':
                badge_color = COLORS['success']
            elif status == 'unavailable':
                badge_color = COLORS['text_darker']
            else:
                badge_color = COLORS['accent']
            status_badge = ctk.CTkFrame(
                header_frame,
                fg_color=badge_color,
                corner_radius=10
            )
            status_badge.pack(side="right")
            ctk.CTkLabel(
                status_badge,
                text=status.title(),
                font=("Segoe UI", 9, "bold"),
                text_color=COLORS['text']
            ).pack(padx=10, pady=4)
        if 'error' in data:
            error_frame = ctk.CTkFrame(
                card_inner,
                fg_color=COLORS['bg'],
                corner_radius=5
            )
            error_frame.pack(fill="x", pady=2)
            error_inner = ctk.CTkFrame(error_frame, fg_color="transparent")
            error_inner.pack(fill="x", padx=10, pady=8)
            ctk.CTkLabel(
                error_inner,
                text=data['error'],
                font=("Segoe UI", 10),
                text_color=COLORS['danger'],
                anchor="w",
                wraplength=500
            ).pack(fill="x")
        if 'note' in data:
            note_frame = ctk.CTkFrame(
                card_inner,
                fg_color=COLORS['bg'],
                corner_radius=5
            )
            note_frame.pack(fill="x", pady=2)
            note_inner = ctk.CTkFrame(note_frame, fg_color="transparent")
            note_inner.pack(fill="x", padx=10, pady=8)
            ctk.CTkLabel(
                note_inner,
                text=f"ℹ️ {data['note']}",
                font=("Segoe UI", 9),
                text_color=COLORS['text_dim'],
                anchor="w",
                wraplength=500
            ).pack(fill="x")
        index = 0
        for key, value in data.items():
            if key in ['error', 'note', 'status', 'service']:
                continue
            if key == 'operator':
                value_color = COLORS['accent']
            elif value == 'Available':
                value_color = COLORS['success']
            else:
                value_color = COLORS['text']
            self.add_detail_row_styled(
                card_inner,
                key.replace('_', ' ').title(),
                str(value),
                index,
                value_color
            )
            index += 1
    def create_social_media_card(self, data: dict):
        card = ctk.CTkFrame(
            self.results_container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        card.pack(fill="x", pady=5)
        card_inner = ctk.CTkFrame(card, fg_color="transparent")
        card_inner.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(
            card_inner,
            text="Social Media Search",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS['text'],
            anchor="w"
        ).pack(anchor="w", pady=(0, 10))
        index = 0
        for platform, info in data.items():
            if isinstance(info, dict) and 'url' in info:
                bg_color = COLORS['bg'] if index % 2 == 0 else COLORS['surface_solid']
                row = ctk.CTkFrame(
                    card_inner,
                    fg_color=bg_color,
                    corner_radius=5,
                    height=32
                )
                row.pack(fill="x", pady=1)
                row.pack_propagate(False)
                content = ctk.CTkFrame(row, fg_color="transparent")
                content.pack(fill="both", expand=True, padx=10, pady=5)
                ctk.CTkLabel(
                    content,
                    text=platform.title(),
                    font=("Segoe UI", 10, "bold"),
                    text_color=COLORS['text'],
                    anchor="w",
                    width=100
                ).pack(side="left")
                link_button = ctk.CTkButton(
                    content,
                    text=info['url'],
                    command=lambda u=info['url']: self.open_url(u),
                    font=("Segoe UI", 9),
                    fg_color="transparent",
                    hover_color=COLORS['surface_light'],
                    text_color=COLORS['accent'],
                    anchor="w",
                    corner_radius=3,
                    height=20,
                    border_width=0
                )
                link_button.pack(side="left", fill="x", expand=True)
                index += 1
    def create_google_card(self, data: dict):
        card = ctk.CTkFrame(
            self.results_container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        card.pack(fill="x", pady=5)
        card_inner = ctk.CTkFrame(card, fg_color="transparent")
        card_inner.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(
            card_inner,
            text="Google Search",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS['text'],
            anchor="w"
        ).pack(anchor="w", pady=(0, 10))
        if 'queries' in data:
            index = 0
            for query_type, url in data['queries'].items():
                bg_color = COLORS['bg'] if index % 2 == 0 else COLORS['surface_solid']
                row = ctk.CTkFrame(
                    card_inner,
                    fg_color=bg_color,
                    corner_radius=5,
                    height=32
                )
                row.pack(fill="x", pady=1)
                row.pack_propagate(False)
                content = ctk.CTkFrame(row, fg_color="transparent")
                content.pack(fill="both", expand=True, padx=10, pady=5)
                ctk.CTkLabel(
                    content,
                    text=query_type.title(),
                    font=("Segoe UI", 10, "bold"),
                    text_color=COLORS['text'],
                    anchor="w",
                    width=100
                ).pack(side="left")
                link_button = ctk.CTkButton(
                    content,
                    text="Open in Browser",
                    command=lambda u=url: self.open_url(u),
                    font=("Segoe UI", 9),
                    fg_color="transparent",
                    hover_color=COLORS['surface_light'],
                    text_color=COLORS['accent'],
                    anchor="w",
                    corner_radius=3,
                    height=20,
                    border_width=0
                )
                link_button.pack(side="left")
                index += 1
        if 'note' in data:
            note_frame = ctk.CTkFrame(
                card_inner,
                fg_color=COLORS['bg'],
                corner_radius=5
            )
            note_frame.pack(fill="x", pady=(5, 0))
            note_inner = ctk.CTkFrame(note_frame, fg_color="transparent")
            note_inner.pack(fill="x", padx=10, pady=8)
            ctk.CTkLabel(
                note_inner,
                text=f"ℹ️ {data['note']}",
                font=("Segoe UI", 9),
                text_color=COLORS['text_dim'],
                anchor="w",
                wraplength=500
            ).pack(fill="x")
    def create_hlr_card(self, hlr):
        card = ctk.CTkFrame(
            self.results_container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        card.pack(fill="x", pady=5)
        card_inner = ctk.CTkFrame(card, fg_color="transparent")
        card_inner.pack(fill="x", padx=20, pady=15)
        header_frame = ctk.CTkFrame(card_inner, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            header_frame,
            text="HLR Lookup",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS['text'],
            anchor="w"
        ).pack(side="left")
        if 'error' not in hlr and hlr.get('status') == 'Available':
            status_badge = ctk.CTkFrame(
                header_frame,
                fg_color=COLORS['success'],
                corner_radius=10
            )
            status_badge.pack(side="right")
            ctk.CTkLabel(
                status_badge,
                text="Online",
                font=("Segoe UI", 9, "bold"),
                text_color=COLORS['text']
            ).pack(padx=10, pady=4)
        if 'error' in hlr:
            error_frame = ctk.CTkFrame(
                card_inner,
                fg_color=COLORS['bg'],
                corner_radius=5
            )
            error_frame.pack(fill="x", pady=2)
            error_inner = ctk.CTkFrame(error_frame, fg_color="transparent")
            error_inner.pack(fill="x", padx=10, pady=8)
            ctk.CTkLabel(
                error_inner,
                text="Status:",
                font=("Segoe UI", 9),
                text_color=COLORS['text_darker'],
                anchor="w",
                width=120
            ).pack(side="left")
            ctk.CTkLabel(
                error_inner,
                text=hlr.get('error', 'Failed'),
                font=("Segoe UI", 10),
                text_color=COLORS['danger'],
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
            if 'note' in hlr:
                note_frame = ctk.CTkFrame(
                    card_inner,
                    fg_color=COLORS['surface_solid'],
                    corner_radius=5
                )
                note_frame.pack(fill="x", pady=2)
                note_inner = ctk.CTkFrame(note_frame, fg_color="transparent")
                note_inner.pack(fill="x", padx=10, pady=8)
                ctk.CTkLabel(
                    note_inner,
                    text="Note:",
                    font=("Segoe UI", 9),
                    text_color=COLORS['text_darker'],
                    anchor="w",
                    width=120
                ).pack(side="left")
                ctk.CTkLabel(
                    note_inner,
                    text=hlr['note'],
                    font=("Segoe UI", 9),
                    text_color=COLORS['text_dim'],
                    anchor="w",
                    wraplength=400
                ).pack(side="left", fill="x", expand=True)
        else:
            index = 0
            for key, value in hlr.items():
                if key not in ['error', 'note', 'available']:
                    if key == 'status':
                        value_color = COLORS['success'] if value == 'Available' else COLORS['text']
                    elif key == 'operator':
                        value_color = COLORS['accent']
                    else:
                        value_color = COLORS['text']
                    self.add_detail_row_styled(
                        card_inner,
                        key.replace('_', ' ').title(),
                        str(value),
                        index,
                        value_color
                    )
                    index += 1
    def add_detail_row_styled(self, parent, label, value, index, value_color=None):
        if value_color is None:
            value_color = COLORS['text']
        bg_color = COLORS['bg'] if index % 2 == 0 else COLORS['surface_solid']
        row = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=5,
            height=32
        )
        row.pack(fill="x", pady=1)
        row.pack_propagate(False)
        content = ctk.CTkFrame(row, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(
            content,
            text=f"{label}:",
            font=("Segoe UI", 9),
            text_color=COLORS['text_darker'],
            anchor="w",
            width=120
        ).pack(side="left")
        ctk.CTkLabel(
            content,
            text=value,
            font=("Segoe UI", 10, "bold" if value_color != COLORS['text'] else "normal"),
            text_color=value_color,
            anchor="w"
        ).pack(side="left", fill="x", expand=True)
    def create_messenger_card(self, online, phone_number):
        card = ctk.CTkFrame(
            self.results_container,
            fg_color=COLORS['surface_solid'],
            corner_radius=8,
            border_width=1,
            border_color=COLORS['border']
        )
        card.pack(fill="x", pady=5)
        card_inner = ctk.CTkFrame(card, fg_color="transparent")
        card_inner.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(
            card_inner,
            text="Messenger Status",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS['text'],
            anchor="w"
        ).pack(anchor="w", pady=(0, 10))
        messenger_links = {
            'telegram': f'https://t.me/{phone_number}',
            'whatsapp': f'https://wa.me/{phone_number}',
            'viber': f'viber://chat?number={phone_number}',
            'signal': f'https://signal.me/#p/{phone_number}'
        }
        index = 0
        for messenger, data in online.items():
            registered = data.get('registered')
            if registered == True:
                status_text = "Registered"
                status_color = COLORS['success']
            elif registered == False:
                status_text = "Not Registered"
                status_color = COLORS['danger']
            else:
                status_text = "Unknown (API not configured)"
                status_color = COLORS['text_darker']
            bg_color = COLORS['bg'] if index % 2 == 0 else COLORS['surface_solid']
            row = ctk.CTkFrame(
                card_inner,
                fg_color=bg_color,
                corner_radius=5,
                height=32
            )
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)
            content = ctk.CTkFrame(row, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=10, pady=5)
            ctk.CTkLabel(
                content,
                text=messenger.title(),
                font=("Segoe UI", 10, "bold"),
                text_color=COLORS['text'],
                anchor="w",
                width=80
            ).pack(side="left")
            ctk.CTkLabel(
                content,
                text=status_text,
                font=("Segoe UI", 10),
                text_color=status_color,
                anchor="w",
                width=200
            ).pack(side="left")
            link_url = messenger_links.get(messenger, '')
            if link_url:
                link_button = ctk.CTkButton(
                    content,
                    text=link_url,
                    command=lambda u=link_url: self.open_url(u),
                    font=("Segoe UI", 9),
                    fg_color="transparent",
                    hover_color=COLORS['surface_light'],
                    text_color=COLORS['accent'],
                    anchor="w",
                    corner_radius=3,
                    height=20,
                    border_width=0
                )
                link_button.pack(side="left", fill="x", expand=True)
            index += 1
    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)
    def add_detail_row_alternating(self, parent, label, value, index):
        bg_color = COLORS['bg'] if index % 2 == 0 else COLORS['surface_solid']
        row = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=5,
            height=32
        )
        row.pack(fill="x", pady=1)
        row.pack_propagate(False)
        content = ctk.CTkFrame(row, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(
            content,
            text=f"{label}:",
            font=("Segoe UI", 9),
            text_color=COLORS['text_darker'],
            anchor="w",
            width=120
        ).pack(side="left")
        value_str = str(value)
        if value == True or value_str.lower() == 'true':
            value_color = COLORS['success']
            value_str = "True"
        elif value == False or value_str.lower() == 'false':
            value_color = COLORS['danger']
            value_str = "False"
        else:
            value_color = COLORS['text']
        ctk.CTkLabel(
            content,
            text=value_str,
            font=("Segoe UI", 10),
            text_color=value_color,
            anchor="w"
        ).pack(side="left", fill="x", expand=True)
    def update_status(self, message, progress):
        self.status_label.configure(text=message)
        self.progress_bar.set(progress)
    def stop_check(self):
        self.checking = False
        self.update_status("Stopped", 0.0)
        self.stop_btn.configure(state="disabled")
    def clear_results(self):
        for widget in self.results_container.winfo_children():
            widget.destroy()
        self.result_data = None
        self.update_status("Ready", 0.0)