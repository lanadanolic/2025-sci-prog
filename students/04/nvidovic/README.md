
# News Scraper

This script scrapes the front page of a news portal (index.hr) to extract the top 5 news headlines and generate a summary of the day's news.

## Scraped URL

- **URL:** `https://www.index.hr`
- **Reason:** This is a popular news portal in Croatia, and its front page provides a good overview of the most important news of the day.

## How to Run

1.  **Create a `.env` file:**

    Create a file named `.env` in the root directory of the project and add your API keys:

    ```
    STEEL_API_KEY="your_steel_api_key"
    GOOGLE_API_KEY="your_google_api_key"
    ```

2.  **Run the script:**

    ```bash
    python scraper.py
    ```

## Pull Request Information

Copy the output from the marimo app into the Pull Request description.

### Scraped URL:

`https://www.index.hr`

### Steel output (isječak):

(Copy the first ~300-500 characters of the raw text from the marimo output here)

### LLM rezultat:

(Copy the summary from the marimo output here)
