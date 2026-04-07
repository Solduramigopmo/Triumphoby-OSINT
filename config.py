COLORS = {
    'bg': '#0f0f14',
    'surface': 'rgba(18, 18, 26, 0.7)',
    'surface_solid': '#12121a',
    'surface_light': '#1a1a28',
    'accent': '#6366f1',
    'accent_hover': '#818cf8',
    'accent_dark': '#4f46e5',
    'success': '#10b981',
    'danger': '#ef4444',
    'warning': '#f59e0b',
    'text': '#e5e7eb',
    'text_dim': '#9ca3af',
    'text_darker': '#6b7280',
    'border': '#2a2a3a',
    'border_light': '#3a3a4a',
}
SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "Bing": "https://www.bing.com/search?q=",
    "DuckDuckGo": "https://duckduckgo.com/html/?q=",
    "Yandex": "https://yandex.com/search/?text=",
    "Baidu": "https://www.baidu.com/s?wd="
}
DORK_TEMPLATES = [
    '{keyword}',
    'intext:"{keyword}"',
    'intitle:"{keyword}"',
    'inurl:{keyword}',
    'filetype:pdf {keyword}',
    'filetype:doc {keyword}',
    'filetype:xls {keyword}',
    'filetype:ppt {keyword}',
    'filetype:txt {keyword}',
    '{keyword} site:gov',
    '{keyword} site:edu',
    '{keyword} site:org',
    'related:{keyword}',
    'cache:{keyword}',
    '"{keyword}" news',
    '"{keyword}" wiki',
    '{keyword} -site:wikipedia.org',
    'allintitle:{keyword}',
    'allintext:{keyword}',
    'allinurl:{keyword}'
]
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_CAPTION_COLOR = 35
DEFAULT_SETTINGS = {
    'transparency': 0.95,
    'bg_opacity': 0.95,
    'blur_type': 'Standard',
    'proxy_enabled': False,
    'proxy_http': '',
    'proxy_https': '',
    'timeout': 15,
    'max_results': 20,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'delay_between_requests': 2
}
SETTINGS_FILE = "settings.json"