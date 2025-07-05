# SeriesDL

A powerful command-line tool for downloading TV series and movies with an intuitive interface.

```
╔══════════════════════════════════════════════════════╗
║                      SeriesDL                        ║
║              made with ♥️ by halid2ud                ║
╚══════════════════════════════════════════════════════╝
```

## Features

- 🔍 **Smart Search**: Find TV series and movies quickly
- 📺 **Multi-format Support**: Download episodes and movies
- 🌐 **Language Options**: German and English support
- 🎯 **Flexible Selection**: Choose specific episodes, seasons, or ranges
- ⚡ **Fast Downloads**: Concurrent downloading with progress tracking
- 🎨 **Rich Interface**: Beautiful console interface with tables and progress bars
- ⚙️ **Configurable**: Customizable settings and preferences
- 🔄 **Auto-retry**: Automatic retry on failed downloads
- 📊 **Session Statistics**: Track your download activity

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Quick Setup

1. **Clone the repository:**
```bash
git clone https://github.com/halid2ud/SeriesDL.git
cd SeriesDL
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python main.py
```

## Requirements

Create a `requirements.txt` file with:

```
requests>=2.28.0
cloudscraper>=1.2.60
beautifulsoup4>=4.11.0
rich>=13.0.0
```

## Usage

### Basic Usage

1. **Run the application:**
```bash
python main.py
```

2. **First-time setup:**
   - Configure your download folder
   - Set default language (German/English)
   - Choose preferred streaming host
   - Set other preferences

3. **Search for content:**
   - Enter the name of a TV series or movie
   - Select from search results
   - Choose what to download (episodes/movies/both)

### Episode Selection Examples

- **Single episode:** `4` (downloads episode 4)
- **Episode range:** `1-5` (downloads episodes 1 through 5)
- **Multiple episodes:** `1,3,5,7` (downloads episodes 1, 3, 5, and 7)
- **Mixed selection:** `1-3,5,8-10` (downloads episodes 1,2,3,5,8,9,10)
- **Entire season:** `s1` (downloads all episodes from season 1)
- **All episodes:** `all` (downloads everything)

### Configuration

The application creates a `settings.json` file with the following options:

```json
{
    "download_folder": "downloads",
    "default_language": "German",
    "default_host": "",
    "clear_console": true,
    "timeout": 30,
    "max_concurrent_downloads": 3,
    "retry_attempts": 3,
    "delay_between_downloads": 0.5
}
```

## Project Structure

```
SeriesDL/
├── main.py                 # Entry point
├── app.py                  # Main application logic
├── config.py               # Configuration settings
├── settings.py             # Settings manager
├── utils.py                # Utility functions
├── models/
│   ├── episode.py          # Episode data model
│   └── movie.py            # Movie data model
├── core/
│   ├── search.py           # Search functionality
│   └── download_manager.py # Download handling
├── network/
│   ├── scraper.py          # Web scraping
│   └── downloader.py       # Download
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features in Detail

### Search Functionality
- Real-time search with relevance scoring
- Cached results for faster repeated searches
- Fuzzy matching for better search results

### User Interface
- Rich console interface with colors and formatting
- Interactive prompts with validation
- Progress bars and spinners
- Detailed error messages and help text

### Content Organization
- Automatic filename generation
- Sanitized filenames for cross-platform compatibility
- Organized folder structure
- Metadata preservation

## Error Handling

The application includes comprehensive error handling:

- Network connection issues
- Invalid user input
- File system errors
- Parsing errors
- Download failures

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

### Setting up Development Environment

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and modular

## Troubleshooting

### Common Issues

**Q: "Module not found" errors**
A: Run `pip install -r requirements.txt` to install all dependencies

**Q: Downloads failing**
A: Check your internet connection and try a different host

**Q: Permission errors**
A: Ensure you have write permissions in the download folder

**Q: Search returns no results**
A: Try different search terms or check if the service is accessible

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Please respect copyright laws and terms of service of the platforms you access. The authors are not responsible for any misuse of this software.

## Support

If you encounter issues or have questions:

1. Check the troubleshooting section
2. Search existing issues on GitHub
3. Create a new issue with detailed information
4. Include error messages and steps to reproduce

## Acknowledgments

- Built with Python and the Rich library for beautiful console output
- Uses cloudscraper for web scraping capabilities
- Inspired by the need for a simple, efficient download tool

---

**Made with ♥️ by halid2ud**
