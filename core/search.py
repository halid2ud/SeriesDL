import re
import html
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, quote_plus
from bs4 import BeautifulSoup
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from config import Config
from models.episode import Episode
from models.movie import Movie
from network.scraper import SeriesScraper
import threading
from collections import defaultdict

class SeriesSearcher:
    def __init__(self, console: Console, settings_manager):
        self.console = console
        self.settings_manager = settings_manager
        import cloudscraper
        self.session = cloudscraper.create_scraper()
        self.session.headers.update(Config.DEFAULT_HEADERS)
        self.base_url = Config.SERIES_URL
        self.scraper = SeriesScraper(self.session)
        self._cache = {}
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def display_banner(self):
        from utils import clear_console
        clear_console()
        banner = """
     _____           _           _____  _      
    / ____|         (_)         |  __ \| |     
    | (___   ___ _ __ _  ___  ___| |  | | |     
     \___ \ / _ \ '__| |/ _ \/ __| |  | | |     
     ____) |  __/ |  | |  __/\__ \ |__| | |____ 
    |_____/ \___|_|  |_|\___||___/_____/|______|
                                                                              
    made with ♥ by halid2ud
    """
        self.console.print(f"[banner]{banner}[/banner]", highlight=False)

    def search_series(self, query: str) -> List[Dict]:
        cache_key = f"search_{query.lower()}"
        with self.lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

        url = f"{self.base_url}/ajax/search"
        headers = {
            'Referer': f"{self.base_url}/search?q={quote_plus(query)}",
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(f"Searching: {query}", total=None)
            try:
                res = self.session.post(url, headers=headers, data={'keyword': query}, timeout=Config.TIMEOUT)
                res.raise_for_status()
                
                results = []
                seen_titles = set()
                for item in res.json():
                    if item.get('link', '').startswith('/serie/stream/') and '/' not in item['link'][14:]:
                        title = html.unescape(re.sub(r'<[^>]+>', '', item.get('title', ''))).strip()
                        if title.lower() not in seen_titles:
                            seen_titles.add(title.lower())
                            results.append({
                                'title': title,
                                'url': urljoin(self.base_url, item['link']),
                                'relevance': self._calculate_relevance(query, title)
                            })

                results.sort(key=lambda x: x['relevance'], reverse=True)
                with self.lock:
                    self._cache[cache_key] = results
                return results[:10]

            except Exception as e:
                self.console.print(f"[red]Search error: {e}[/red]")
                return []

    def _calculate_relevance(self, query: str, title: str) -> float:
        query_lower = query.lower()
        title_lower = title.lower()
        
        if query_lower == title_lower:
            return 1.0
        if title_lower.startswith(query_lower):
            return 0.9
        if query_lower in title_lower:
            return 0.8
        
        query_words = set(query_lower.split())
        title_words = set(title_lower.split())
        overlap = len(query_words & title_words)
        return 0.5 + (overlap / len(query_words)) * 0.3 if overlap > 0 else 0.1

    def show_search_results(self, results: List[Dict]) -> Optional[Dict]:
        if not results:
            return None

        table = Table(title="Search Results", show_header=True, header_style="bold magenta")
        table.add_column("#", width=3, style="cyan")
        table.add_column("Title", style="bold white")
        table.add_column("Relevance", width=10, style="green")

        for i, res in enumerate(results, 1):
            table.add_row(str(i), res['title'], f"{res['relevance']:.1%}")

        self.console.print(table)
        
        try:
            choice = IntPrompt.ask("[bold cyan]Select number (0 to cancel)[/bold cyan]", default=1)
            return results[choice - 1] if 1 <= choice <= len(results) else None
        except (KeyboardInterrupt, EOFError):
            return None

    def get_series_details(self, url: str) -> Dict:
        return self.scraper.scrape_series_details(url)

    def show_series_info(self, details: Dict):
        from rich.layout import Layout
        from rich.panel import Panel
        from rich.align import Align

        layout = Layout()
        layout.split_column(
            Layout(name="header", size=8),
            Layout(name="stats", size=5),
            Layout(name="links", size=3)
        )

        header_text = f"[bold white]{details['title']}[/bold white]"
        if details['timeline']:
            header_text += f"\n[dim cyan]{details['timeline']}[/dim cyan]"

        stats_text = f"[green]Episodes:[/green] {details['episode_count']}\n" + \
                     f"[cyan]Seasons:[/cyan] {details['total_seasons']}"
        if details['movie_count']:
            stats_text += f"\n[yellow]Movies:[/yellow] {details['movie_count']}"

        links_text = f"[blue]IMDB:[/blue] [link={details['imdb_link']}]{details['imdb_link']}[/link]" \
                     if details['imdb_link'] else "[dim]No external links[/dim]"

        layout["header"].update(Panel(Align.center(header_text), title="[bold magenta]Series Information[/bold magenta]", border_style="magenta"))
        layout["stats"].update(Panel(Align.center(stats_text), title="[bold blue]Statistics[/bold blue]", border_style="blue"))
        layout["links"].update(Panel(Align.center(links_text), title="[bold green]Links[/bold green]", border_style="green"))

        self.console.print(layout)

    def select_series_language(self, _details: Dict) -> str:
        default_lang = self.settings_manager.settings.get('default_language', 'German')
        if default_lang in ['Ger Dub', 'German', 'Deutsch']:
            default_lang = 'German'
        elif default_lang in ['Eng Dub', 'English']:
            default_lang = 'English'

        if Prompt.ask(f"[bold cyan]Use default language ({default_lang})?[/bold cyan]", default=True):
            return default_lang

        return Prompt.ask(
            "[bold cyan]Select Language[/bold cyan]",
            choices=["German", "English"],
            default=default_lang
        )

    def show_detailed_series_info(self, details: Dict, lang: str):
        if details['episodes']:
            seasons = defaultdict(list)
            for ep in details['episodes']:
                seasons[ep.season].append(ep)

            table = Table(title=f"Episodes Overview ({lang})", show_header=True, header_style="bold green")
            table.add_column("Season", width=8, style="cyan")
            table.add_column("Episodes", width=10, style="yellow")
            table.add_column("Range", style="white")

            for season in sorted(seasons.keys()):
                eps = sorted(seasons[season], key=lambda x: x.episode)
                table.add_row(f"Season {season}", str(len(eps)), f"E{eps[0].episode:02d}-E{eps[-1].episode:02d}")

            self.console.print(table)

        if details['movies']:
            movie_table = Table(title=f"Movies ({lang})", show_header=True, header_style="bold yellow")
            movie_table.add_column("#", width=3, style="yellow")
            movie_table.add_column("Title", style="white")

            for movie in sorted(details['movies'], key=lambda x: x.movie):
                movie_table.add_row(str(movie.movie), movie.title)

            self.console.print(movie_table)

    def select_series_episodes(self, details: Dict) -> List:
        has_episodes = bool(details.get('episodes'))
        has_movies = bool(details.get('movies'))
        
        if not has_episodes and not has_movies:
            self.console.print("[red]No content available for download.[/red]")
            return []
        
        if has_episodes and not has_movies:
            content_type = "episodes"
        elif has_movies and not has_episodes:
            content_type = "movies"
        else:
            content_type = Prompt.ask(
                "[bold cyan]What to download?[/bold cyan]",
                choices=["episodes", "movies", "both"],
                default="episodes"
            )

        selected = []
        
        if content_type in ["episodes", "both"] and details['episodes']:
            episodes = sorted(details['episodes'], key=lambda x: (x.season, x.episode))
            
            seasons = defaultdict(list)
            for ep in episodes:
                seasons[ep.season].append(ep)
            
            self.console.print("[dim]Available episodes:[/dim]")
            for season in sorted(seasons.keys()):
                eps = sorted(seasons[season], key=lambda x: x.episode)
                ep_range = f"E{eps[0].episode:02d}-E{eps[-1].episode:02d}"
                self.console.print(f"[dim]Season {season}: {ep_range}[/dim]")
            
            ep_input = Prompt.ask(
                "[bold cyan]Which episodes? (e.g., 1-3,5 or 'all' or 's1' for season 1)[/bold cyan]",
                default="1"
            )

            if ep_input.lower() == "all":
                selected.extend(episodes)
            elif ep_input.lower().startswith('s'):
                try:
                    season_num = int(re.search(r's(\d+)', ep_input.lower()).group(1))
                    selected.extend([ep for ep in episodes if ep.season == season_num])
                except (AttributeError, ValueError):
                    self.console.print("[red]Invalid season format. Use 's1', 's2', etc.[/red]")
                    return []
            else:
                try:
                    selected_nums = self._parse_episode_range(ep_input)
                    if not selected_nums:
                        return []
                    
                    if len(seasons) > 1:
                        season_choice = IntPrompt.ask(
                            f"[bold cyan]Which season? {sorted(seasons.keys())}[/bold cyan]",
                            default=sorted(seasons.keys())[0]
                        )
                        selected.extend([ep for ep in episodes if ep.season == season_choice and ep.episode in selected_nums])
                    else:
                        selected.extend([ep for ep in episodes if ep.episode in selected_nums])
                except ValueError as e:
                    self.console.print(f"[red]Invalid episode range: {e}[/red]")
                    return []

        if content_type in ["movies", "both"] and details['movies']:
            movies = sorted(details['movies'], key=lambda x: x.movie)
            movie_input = Prompt.ask(
                "[bold cyan]Which movies? (e.g., 1,2 or 'all')[/bold cyan]",
                default="all"
            )
            if movie_input.lower() == "all":
                selected.extend(movies)
            else:
                try:
                    selected_nums = self._parse_episode_range(movie_input)
                    selected.extend([m for m in movies if m.movie in selected_nums])
                except ValueError as e:
                    self.console.print(f"[red]Invalid movie range: {e}[/red]")
                    return []

        return selected

    def _parse_episode_range(self, input_str: str) -> List[int]:
        nums = set()
        try:
            for part in input_str.replace(' ', '').split(','):
                if '-' in part:
                    start_str, end_str = part.split('-', 1)
                    start, end = int(start_str), int(end_str)
                    if start > end:
                        raise ValueError(f"Invalid range: {start}-{end}")
                    nums.update(range(start, end + 1))
                else:
                    nums.add(int(part))
        except ValueError as e:
            raise ValueError(f"Invalid episode range format: {input_str}. Use format like '1-3,5' or '1,2,3'")
        
        return sorted(nums)

    def select_series_host(self, content_item, lang: str) -> Optional[Dict]:
        try:
            res = self.session.get(content_item.url, timeout=Config.TIMEOUT)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')

            if isinstance(content_item, Movie):
                eng_title = soup.select_one('small.episodeEnglishTitle')
                if eng_title:
                    content_item.english_title = eng_title.text.strip()

            lang_key = "1" if lang == "German" else "2"
            hosts = []
            
            for link in soup.select('a.watchEpisode'):
                parent = link.find_parent('li')
                if parent and parent.get('data-lang-key') == lang_key:
                    icon = link.select_one('i[class*="icon"]')
                    host_name = next((cls.replace('icon-', '').title() 
                                    for cls in icon.get('class', []) 
                                    if cls != 'icon'), "Unknown")
                    href = urljoin(self.base_url, link['href']) if not link['href'].startswith('http') else link['href']
                    hosts.append({'name': host_name, 'url': href})

            if not hosts:
                for link in soup.select('a[href*="/redirect/"]'):
                    parent = link.find_parent('li')
                    if parent and parent.get('data-lang-key') == lang_key:
                        href = urljoin(self.base_url, link['href']) if not link['href'].startswith('http') else link['href']
                        hosts.append({'name': 'Stream', 'url': href})

            if not hosts:
                return None

            preferred_host = self.settings_manager.settings.get('default_host', '')
            if preferred_host:
                for host in hosts:
                    if host['name'].lower() == preferred_host.lower():
                        return host

            if len(hosts) == 1:
                return hosts[0]

            table = Table(title=f"Select Host ({lang})", show_header=True, header_style="bold blue")
            table.add_column("#", width=3, style="blue")
            table.add_column("Host", style="white")

            for i, host in enumerate(hosts, 1):
                table.add_row(str(i), host['name'])

            self.console.print(table)
            choice = IntPrompt.ask("[bold cyan]Choose host[/bold cyan]", default=1)
            selected = hosts[choice - 1] if 1 <= choice <= len(hosts) else None

            if selected and Prompt.ask(f"[cyan]Save '{selected['name']}' as default?[/cyan]", default=False):
                self.settings_manager.settings['default_host'] = selected['name']
                self.settings_manager.save()

            return selected

        except Exception as e:
            self.console.print(f"[red]Host selection error: {e}[/red]")
            return None