from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from config import Config
from settings import SettingsManager
from core.search import SeriesSearcher
from core.download_manager import DownloadManager
from utils import clear_console

class SeriesDLApp:
    def __init__(self):
        self.console = Console(theme=Config.CONSOLE_THEME)
        self.settings = SettingsManager(console=self.console)
        self.searcher = SeriesSearcher(console=self.console, settings_manager=self.settings)
        self.downloader = DownloadManager(console=self.console, settings_manager=self.settings)
        self.session_stats = {'searches': 0, 'downloads': 0, 'errors': 0}

    def run(self):
        """Main application loop"""
        try:
            self.searcher.display_banner()

            if self._should_show_settings():
                self.settings.show_settings_menu()
                self.console.print("\n[green]Settings configured! Starting SeriesDL...[/green]\n")
                clear_console()
            
            while True:
                try:
                    self._update_stats_display()
                    
                    query = Prompt.ask(
                        "[bold cyan]Search for a series (or 'quit' to exit)[/bold cyan]"
                    ).strip()
                    
                    if query.lower() in ['quit', 'exit', 'q']:
                        self._show_goodbye_message()
                        break
                    
                    if not query:
                        continue
                    
                    self.session_stats['searches'] += 1
                    
                    if self._process_series_search(query):
                        self.session_stats['downloads'] += 1
                    
                    if not self._ask_continue():
                        self._show_goodbye_message()
                        break
                        
                except KeyboardInterrupt:
                    self._handle_keyboard_interrupt()
                    break
                except Exception as e:
                    self.session_stats['errors'] += 1
                    self.console.print(f"[red]Unexpected error: {e}[/red]")
                    continue
                    
        except Exception as e:
            self.console.print(f"[red]Fatal error: {e}[/red]")

    def _should_show_settings(self) -> bool:
        """Check if settings should be shown at startup"""
        import os
        settings_file = self.settings.filename

        if not os.path.exists(settings_file):
            self.console.print("[yellow]Welcome to SeriesDL! Let's configure your settings first.[/yellow]")
            return True
        
        return Confirm.ask(
            "[bold cyan]Review/modify settings before starting?[/bold cyan]",
            default=False
        )
    
    def _show_goodbye_message(self):
        """Show goodbye message with session stats"""
        stats_text = f"[green]Session Statistics:[/green]\n"
        stats_text += f"• Searches: {self.session_stats['searches']}\n"
        stats_text += f"• Downloads: {self.session_stats['downloads']}\n"
        if self.session_stats['errors'] > 0:
            stats_text += f"• Errors: {self.session_stats['errors']}\n"
        
        goodbye_panel = Panel(
            f"[bold yellow]Thanks for using SeriesDL![/bold yellow]\n\n{stats_text}\n"
            "[dim]See you next time![/dim]",
            title="[bold cyan]Goodbye![/bold cyan]",
            border_style="cyan"
        )
        self.console.print(goodbye_panel)
    
    def _update_stats_display(self):
        """Update session statistics display"""
        if self.session_stats['searches'] > 0:
            stats = f"[dim]Session: {self.session_stats['searches']} searches, {self.session_stats['downloads']} downloads[/dim]"
            self.console.print(stats)
    
    def _process_series_search(self, query: str) -> bool:
        """Process a series search and download"""
        try:
            results = self.searcher.search_series(query)
            if not results:
                self.console.print("[red]No results found.[/red]")
                return False
            
            selected = self.searcher.show_search_results(results)
            if not selected:
                self.console.print("[yellow]No series selected.[/yellow]")
                return False
            
            details = self.searcher.get_series_details(selected['url'])
            if not details or (not details.get('episodes') and not details.get('movies')):
                self.console.print("[red]No content found for this series.[/red]")
                return False
            
            self.searcher.show_series_info(details)
            lang = self.searcher.select_series_language(details)
            if not lang:
                self.console.print("[yellow]No language selected.[/yellow]")
                return False
            
            self.searcher.show_detailed_series_info(details, lang)
            selected_content = self.searcher.select_series_episodes(details)
            if not selected_content:
                self.console.print("[red]No content selected for download.[/red]")
                return False
            
            host_info = self.searcher.select_series_host(selected_content[0], lang)
            if not host_info:
                self.console.print("[red]No valid host selected.[/red]")
                return False
            
            self.downloader.download_series_episodes(details, selected_content, lang, host_info)
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error processing search: {e}[/red]")
            return False
    
    def _ask_continue(self) -> bool:
        """Ask user if they want to continue"""
        try:
            again = Prompt.ask(
                "[bold cyan]Download more series?[/bold cyan]",
                choices=["y", "n"],
                default="y"
            )
            return again.lower() == "y"
        except (KeyboardInterrupt, EOFError):
            return False
    
    def _handle_keyboard_interrupt(self):
        """Handle keyboard interrupt gracefully"""
        self.console.print("\n[bold red]Interrupted by user[/bold red]")
        self._show_goodbye_message()