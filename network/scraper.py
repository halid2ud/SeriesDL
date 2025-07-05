import re
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress
from config import Config
from models.episode import Episode
from models.movie import Movie

class SeriesScraper:
    def __init__(self, session):
        self.session = session
        self.base_url = Config.SERIES_URL
        self.logger = logging.getLogger(__name__)

    def scrape_series_details(self, url: str) -> Dict:
        """Full scraping pipeline for series details"""
        with Progress() as progress:
            task = progress.add_task("Scraping...", total=100)
            try:
                # Fetch initial page
                res = self.session.get(url, timeout=Config.TIMEOUT)
                res.raise_for_status()
                soup = BeautifulSoup(res.text, 'html.parser')
                progress.update(task, advance=20)

                # Extract metadata
                title = soup.select_one('.series-title span').text.strip() if soup.select_one('.series-title span') else "Unknown"
                timeline = self._extract_timeline(soup)
                imdb_link = self._extract_imdb_link(soup)
                progress.update(task, advance=10)

                # Get seasons and episodes
                seasons = self._get_all_seasons(soup)
                progress.update(task, advance=20)
                episodes = self._scrape_episodes(seasons)
                progress.update(task, advance=30)

                # Get movies
                movies = self._scrape_movies(url)
                progress.update(task, advance=20)

                return {
                    'title': title,
                    'timeline': timeline,
                    'imdb_link': imdb_link,
                    'episodes': episodes,
                    'movies': movies,
                    'total_seasons': len(seasons),
                    'episode_count': len(episodes),
                    'movie_count': len(movies)
                }

            except Exception as e:
                self.logger.error(f"Scraping failed: {e}")
                return {'title': 'Unknown', 'episodes': [], 'movies': [], 'timeline': '', 'imdb_link': ''}

    def _extract_timeline(self, soup: BeautifulSoup) -> str:
        timeline_tag = soup.select_one('small span[itemprop="startDate"]')
        if timeline_tag:
            start_year = timeline_tag.text.strip()
            end_tag = soup.select_one('small span[itemprop="endDate"]')
            end_year = end_tag.text.strip() if end_tag else "Present"
            return f"({start_year} - {end_year})"
        return ""

    def _extract_imdb_link(self, soup: BeautifulSoup) -> str:
        imdb_tag = soup.select_one('a[data-imdb]')
        return imdb_tag['href'] if imdb_tag else ""

    def _get_all_seasons(self, soup: BeautifulSoup) -> List[Dict]:
        seasons = []
        season_links = soup.select('a[href*="/staffel-"]')
        seen_urls = set()

        for link in season_links:
            href = link['href']
            if href not in seen_urls:
                seen_urls.add(href)
                season_num = int(re.search(r'staffel-(\d+)', href).group(1))
                seasons.append({
                    'season': season_num,
                    'url': urljoin(self.base_url, href)
                })

        return sorted(seasons, key=lambda x: x['season'])

    def _scrape_episodes(self, seasons: List[Dict]) -> List[Episode]:
        episodes = set()

        def fetch_season(season_info):
            try:
                res = self.session.get(season_info['url'], timeout=Config.TIMEOUT)
                res.raise_for_status()
                soup = BeautifulSoup(res.text, 'html.parser')
                
                for link in soup.select('a[href*="/episode-"]'):
                    href = link['href']
                    ep_num = int(re.search(r'episode-(\d+)', href).group(1))
                    episodes.add(Episode(
                        title=f"S{season_info['season']:02d}E{ep_num:02d}",
                        season=season_info['season'],
                        episode=ep_num,
                        url=urljoin(self.base_url, href)
                    ))
            except Exception as e:
                self.logger.error(f"Failed to scrape season {season_info['season']}: {e}")

        with ThreadPoolExecutor(max_workers=3) as executor:
            list(executor.map(fetch_season, seasons))

        return sorted(episodes, key=lambda x: (x.season, x.episode))

    def _scrape_movies(self, base_url: str) -> List[Movie]:
        movies = set()
        try:
            res = self.session.get(base_url + "/filme", timeout=Config.TIMEOUT)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                for link in soup.select('td.seasonEpisodeTitle a[href*="/filme/film-"]'):
                    href = link['href']
                    movie_num = int(re.search(r'film-(\d+)', href).group(1))
                    title = link.select_one('strong').text.strip() if link.select_one('strong') else "Unknown"
                    movies.add(Movie(
                        title=title,
                        movie=movie_num,
                        url=urljoin(self.base_url, href)
                    ))
        except Exception as e:
            self.logger.error(f"Failed to scrape movies: {e}")

        return sorted(movies, key=lambda x: x.movie)