# BBC News Scraper

A Marimo-based scraper that fetches BBC News and generates energetic AI summaries.

## Setup

1. Install dependencies: `pip install marimo requests beautifulsoup4 python-dotenv google-genai`
2. Create `.env` file with your API keys:
```
STEEL_API_KEY=your_steel_key
GEMINI_API_KEY=your_gemini_key
```
3. Run: `marimo edit scraper.py`

## How It Works

Scrapes BBC News using Steel API → Parses HTML with BeautifulSoup → Generates enthusiastic summaries with Gemini AI

## API Keys

- Steel API: [steel.dev](https://steel.dev)
- Gemini API: [aistudio.google.com](https://aistudio.google.com)