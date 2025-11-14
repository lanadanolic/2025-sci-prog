# FBref Football Match Scraper

This scraper fetches football match data from FBref using the Steel API, then processes it with Google's Gemini API to extract structured match information.

## Features

- Fetches match data from FBref using Steel API
- Processes raw HTML/text with Google Gemini AI
- Extracts structured match information including:
  - Match details (teams, score, date, venue)
  - Match statistics (possession, shots, fouls, cards)
  - Player performance data
  - Key match events (goals, cards)

## Setup


1. Get a Steel API key:
   - Visit https://app.steel.dev/quickstart
   - Sign up and get your API key

2. Get a Google Gemini API key:
   - Visit https://makersuite.google.com/app/apikey
   - Create a new API key

3. Set your API keys (optional):
```bash
export STEEL_API_KEY="your-steel-api-key-here"
export GEMINI_API_KEY="your-gemini-api-key-here"
```

Or enter them when prompted by the script.

## Usage

### Basic Usage

Run the scraper with the default match URL:

```bash
python fbref_scraper.py
```

### Custom Match URL

Edit the `match_url` variable in `fbref_scraper.py` to scrape a different match:

```python
match_url = "https://fbref.com/en/matches/[match-id]/..."
```

### Programmatic Usage

```python
from fbref_scraper import FBrefScraper

# Initialize scraper
scraper = FBrefScraper(
    steel_api_key="your-steel-api-key",
    gemini_api_key="your-gemini-api-key"
)

# Scrape and analyze a match
results = scraper.scrape_and_analyze(
    fbref_url="https://fbref.com/en/matches/...",
    output_file="match_analysis.md"
)

# Get the Gemini analysis
print(results['gemini_analysis'])
```

## Output

The scraper generates:
- Console output with the Gemini analysis
- `match_analysis.md` - Markdown file with formatted results (ready for PR)

## Example Match URLs

- Champions League Final 2023: `https://fbref.com/en/matches/920da003/Manchester-City-Inter-June-10-2023-Champions-League`
- Premier League matches: Browse FBref and copy any match URL

## How It Works

1. **Steel API**: Fetches the raw HTML content from the FBref match page using authenticated API calls
2. **Gemini API**: Analyzes the content and extracts structured match data
3. **Output**: Formats the analysis in markdown for easy copying to PR

## For PR Submission

After running the scraper, copy the output between the lines:
```
========================================
GEMINI ANALYSIS RESULT (Copy this for your PR):
========================================
[Copy everything here]
========================================
```

## API Details

### Steel API
- Endpoint: `https://api.steel.dev/v1/scrape`
- Authentication: API key in `x-steel-api-key` header
- Get your key: https://app.steel.dev/quickstart

### Gemini API
- Model used: `gemini-pro`
- Maximum content length: 50,000 characters
- Output token limit: 4,096 tokens
- Get your key: https://makersuite.google.com/app/apikey
