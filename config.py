from rich.theme import Theme

class Config:
    SERIES_URL = "https://s.to"
    TIMEOUT = 30

    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html',
    }

    CONSOLE_THEME = Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "red bold",
        "success": "green bold",
        "highlight": "bold magenta",
        "banner": "bold magenta",
        "input_prompt": "bold cyan"
    })