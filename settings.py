import json
import os
from rich.prompt import Prompt, IntPrompt, Confirm

class SettingsManager:
    def __init__(self, filename='settings.json', console=None):
        self.filename = filename
        self.console = console
        self.settings = {
            "download_folder": "downloads",
            "default_language": "German",
            "default_host": "",
            "clear_console": True,
            "timeout": 30,
            "max_concurrent_downloads": 3,
            "retry_attempts": 3,
            "delay_between_downloads": 0.5
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
                if self.console:
                    self.console.print(f"[green]Settings loaded from {self.filename}[/green]")
            except Exception as e:
                if self.console:
                    self.console.print(f"[yellow]Could not load settings: {e}[/yellow]")

    def save(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f, indent=4)
            if self.console:
                self.console.print(f"[green]Settings saved to {self.filename}[/green]")
        except Exception as e:
            if self.console:
                self.console.print(f"[red]Could not save settings: {e}[/red]")

    def show_settings_menu(self):
        from rich.table import Table
        
        settings_table = Table(title="Current Settings", show_header=True, header_style="bold blue")
        settings_table.add_column("Setting", style="cyan")
        settings_table.add_column("Current Value", style="white")
        settings_table.add_column("Description", style="dim")
        
        descriptions = {
            "download_folder": "Where downloaded files are saved",
            "default_language": "Default language selection",
            "default_host": "Preferred streaming host",
            "clear_console": "Clear console between operations",
            "timeout": "Request timeout in seconds",
            "max_concurrent_downloads": "Maximum simultaneous downloads",
            "retry_attempts": "Number of retry attempts on failure",
            "delay_between_downloads": "Delay between downloads (seconds)"
        }
        
        for key, val in self.settings.items():
            desc = descriptions.get(key, "No description available")
            settings_table.add_row(key, str(val), desc)
        
        if self.console:
            self.console.print(settings_table)
        
        modify = Confirm.ask("[bold cyan]Modify settings?[/bold cyan]", default=False)
        if not modify:
            return
        
        for key, val in self.settings.items():
            if isinstance(val, bool):
                new_val = Confirm.ask(f"[cyan]{key}[/cyan] [{val}]", default=val)
            elif isinstance(val, int):
                new_val = IntPrompt.ask(f"[cyan]{key}[/cyan] [{val}]", default=val)
            else:
                new_val = Prompt.ask(f"[cyan]{key}[/cyan] [{val}]", default=str(val))
            
            self.settings[key] = new_val
        
        self.save()
        if self.console:
            self.console.print("[green]Settings updated successfully![/green]")