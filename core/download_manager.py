import os
import time
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from utils import sanitize_filename
from models.episode import Episode
from network.downloader import download
from models.movie import Movie
from rich.prompt import Confirm

class DownloadManager:
    def __init__(self, console, settings_manager):
        self.console = console
        self.settings_manager = settings_manager

    def download_series_episodes(self, details: dict, content_items: list, lang: str, host_info: dict):
        """Handle downloading of series episodes/movies"""
        download_dir = self.settings_manager.settings.get("download_folder", "downloads")
        os.makedirs(download_dir, exist_ok=True)

        original_dir = os.getcwd()
        os.chdir(download_dir)

        successful_downloads = 0
        failed_downloads = 0

        try:
            self.console.print(f"[bold]Starting download of {len(content_items)} items...[/bold]")
        
            for i, item in enumerate(content_items, 1):
                # Generate filename based on item type
                if isinstance(item, Movie):
                    eng_title = getattr(item, 'english_title', '') or item.title
                    eng_title = eng_title.replace(' ', '_')
                    filename = f"{details['title'].replace(' ', '_')}_Movie_{item.movie}_{eng_title}_{lang}.mp4"
                else:
                    filename = f"{details['title'].replace(' ', '_')}_{item.title}_{lang}.mp4"
            
                filename = sanitize_filename(filename)
                self.console.print(f"[blue]({i}/{len(content_items)}) Downloading: {filename}[/blue]")
            
                # Check if file exists
                if os.path.exists(filename):
                    if not Confirm.ask(f"[yellow]File '{filename}' exists. Overwrite?[/yellow]", default=False):
                        self.console.print(f"[yellow]Skipped: {filename}[/yellow]")
                        continue

                # Download the content
                try:
                    if download(host_info['url']):
                        if os.path.exists(filename) and os.path.getsize(filename) > 0:
                            self.console.print(f"[green]✓ Successfully downloaded: {filename}[/green]")
                            successful_downloads += 1
                        else:
                            self.console.print(f"[red]✗ Failed to download: {filename}[/red]")
                            failed_downloads += 1
                    else:
                        self.console.print(f"[red]✗ Failed to download: {filename}[/red]")
                        failed_downloads += 1
                except Exception as e:
                    self.console.print(f"[red]✗ Failed to download {filename}: {e}[/red]")
                    failed_downloads += 1

                # Delay between downloads
                delay = self.settings_manager.settings.get("delay_between_downloads", 0.5)
                if i < len(content_items) and delay > 0:
                    time.sleep(delay)

            # Show summary
            self.console.print(f"\n[bold green]Download Summary:[/bold green]")
            self.console.print(f"[green]✓ Successful: {successful_downloads}[/green]")
            if failed_downloads > 0:
                self.console.print(f"[red]✗ Failed: {failed_downloads}[/red]")
        
            if successful_downloads > 0:
                self.console.print(f"[green]Files saved to: {os.path.abspath(download_dir)}[/green]")

        except Exception as e:
            self.console.print(f"[red]Download error: {e}[/red]")
        finally:
            os.chdir(original_dir)