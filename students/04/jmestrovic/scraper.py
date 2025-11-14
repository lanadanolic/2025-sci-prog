import json
import os
import subprocess
import sys
from datetime import datetime

# Auto-install requirements if not available
try:
    import requests
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing BeautifulSoup4...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4", "lxml"])
    from bs4 import BeautifulSoup

class FBrefScraper:
    def __init__(self, steel_api_key, gemini_api_key):
        """
        Initialize the FBref scraper with Steel API and Gemini API

        Args:
            steel_api_key: Your Steel API key from https://app.steel.dev
            gemini_api_key: Your Google Gemini API key
        """
        self.steel_api_key = steel_api_key
        self.steel_api_url = "https://api.steel.dev/v1/scrape"
        self.gemini_api_key = gemini_api_key
        self.gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"

    def _direct_scrape_fallback(self, fbref_url, headers):
        """Fallback to simple scrape endpoint"""
        print("Using simple scrape endpoint as fallback...")
        scrape_payload = {
            "url": fbref_url,
            "waitFor": 10000
        }

        response = requests.post(
            "https://api.steel.dev/v1/scrape",
            json=scrape_payload,
            headers=headers,
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            content = data.get('content', {}).get('html', '')
            return content
        return None

    def fetch_with_steel_api(self, fbref_url):
        """
        Fetch content from FBref using Steel API

        Args:
            fbref_url: The FBref match URL to scrape

        Returns:
            The text content from the page
        """
        print(f"Fetching data from: {fbref_url}")
        print("Using Steel API...")

        try:
            # Correct Steel API headers (note: steel-api-key, not x-steel-api-key)
            headers = {
                "Content-Type": "application/json",
                "steel-api-key": self.steel_api_key
            }

            # Create a session first for better control
            print("Creating Steel API session...")
            session_payload = {
                "sessionTimeout": 300000  # 5 minutes
            }

            session_response = requests.post(
                "https://api.steel.dev/v1/sessions",
                json=session_payload,
                headers=headers,
                timeout=30
            )

            if session_response.status_code not in [200, 201]:
                print(f"Failed to create session: {session_response.status_code}")
                print(f"Response: {session_response.text}")
                # Fallback to direct scrape
                return self._direct_scrape_fallback(fbref_url, headers)

            session_data = session_response.json()
            session_id = session_data.get('id')
            print(f"Session created: {session_id}")

            # Navigate to the page
            scrape_payload = {
                "url": fbref_url,
                "sessionId": session_id
            }

            print(f"Navigating to {fbref_url}...")
            scrape_response = requests.post(
                "https://api.steel.dev/v1/scrape",
                json=scrape_payload,
                headers=headers,
                timeout=120
            )

            if scrape_response.status_code == 200:
                # Wait for dynamic content to load
                print("Waiting for stats tables to load...")
                import time
                time.sleep(5)

                # Get the HTML content after waiting
                html_payload = {
                    "sessionId": session_id,
                    "command": "document.documentElement.outerHTML"
                }

                html_response = requests.post(
                    "https://api.steel.dev/v1/sessions/evaluate",
                    json=html_payload,
                    headers=headers,
                    timeout=30
                )

                if html_response.status_code == 200:
                    html_data = html_response.json()
                    content = html_data.get('result', {}).get('value', '')

                    # Release session
                    requests.delete(
                        f"https://api.steel.dev/v1/sessions/{session_id}",
                        headers=headers
                    )

                    if content:
                        print(f"Successfully fetched {len(content)} characters from Steel API")
                        with open('debug_raw_content.html', 'w', encoding='utf-8') as f:
                            f.write(content)
                        print("Saved raw content to debug_raw_content.html")
                        return content

                data = scrape_response.json()
                # Debug: print the response structure
                print(f"Response keys: {list(data.keys())}")

                # Save the full response for debugging
                with open('debug_full_response.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print("Saved full API response to debug_full_response.json")

                # Steel API returns content in different fields - try all possibilities
                content = None

                # Check common field names (prioritize HTML fields first)
                for field in ['html', 'content', 'body', 'data', 'text', 'page_content']:
                    if field in data:
                        value = data[field]
                        # Check if it's a string (direct content)
                        if isinstance(value, str) and value:
                            content = value
                            print(f"Found content in field: {field}")
                            break
                        # Check if it's a dict with nested HTML
                        elif isinstance(value, dict):
                            if 'html' in value and isinstance(value['html'], str):
                                content = value['html']
                                print(f"Found content in nested field: {field}.html")
                                break
                            elif 'content' in value and isinstance(value['content'], str):
                                content = value['content']
                                print(f"Found content in nested field: {field}.content")
                                break
                            elif 'text' in value and isinstance(value['text'], str):
                                content = value['text']
                                print(f"Found content in nested field: {field}.text")
                                break

                # If no direct field, check nested structures in 'data'
                if not content and 'data' in data and isinstance(data['data'], dict):
                    for field in ['html', 'content', 'body', 'text']:
                        if field in data['data']:
                            value = data['data'][field]
                            if isinstance(value, str) and value:
                                content = value
                                print(f"Found content in nested field: data.{field}")
                                break
                            elif isinstance(value, dict) and 'html' in value:
                                content = value['html']
                                print(f"Found content in nested field: data.{field}.html")
                                break

                # Last resort: convert entire response to string
                if not content:
                    print("WARNING: Could not find content in standard fields, using full response")
                    content = str(data)

                if isinstance(content, str):
                    print(f"Successfully fetched {len(content)} characters from Steel API")
                    # Save raw HTML for debugging
                    with open('debug_raw_content.html', 'w', encoding='utf-8') as f:
                        f.write(content)
                    print("Saved raw content to debug_raw_content.html for inspection")

                    # Check if content looks valid (not just error messages)
                    if len(content) < 1000:
                        print("WARNING: Content seems very short, might be an error page")
                        print(f"Content preview: {content[:500]}")
                else:
                    print(f"Content type: {type(content)}")
                    content = str(content)

                return content
            else:
                print(f"Steel API returned status code: {scrape_response.status_code}")
                print(f"Response: {scrape_response.text}")
                return None

        except Exception as e:
            print(f"Error fetching from Steel API: {str(e)}")
            return None

    def process_with_gemini(self, text_content, prompt=None):
        """
        Send the scraped text to Google Gemini API for processing

        Args:
            text_content: The text content to process
            prompt: Optional custom prompt for Gemini

        Returns:
            Gemini's response
        """
        if prompt is None:
            prompt = """You are a football data analyst. I will provide you with structured match data extracted from FBref.

The data includes:
- MATCH SUMMARY section with teams, scores, and basic match info
- TABLE sections with player statistics for both teams
- MATCH EVENTS section with goals, cards, and other key moments

YOUR TASK: Analyze this structured data and CREATE A CLEAN, COMPREHENSIVE MATCH REPORT.

Extract and present the following information in markdown format:

## 1. Match Details
- Home Team:
- Away Team:
- Final Score:
- Date:
- Competition:
- Venue:
- Expected Goals (xG) for both teams if available

## 2. Match Statistics Comparison
Create a table comparing both teams:
| Statistic | Home Team | Away Team |
|-----------|-----------|-----------|
| Possession % | | |
| Total Shots | | |
| Shots on Target | | |
| Corners | | |
| Fouls | | |
| Yellow Cards | | |
| Red Cards | | |

## 3. Top Performers
List the top 3-5 players from EACH team based on:
- Goals scored
- Assists provided
- Key statistics (shots, passes, tackles, saves, etc.)

Format: **Player Name** (Team) - [stats]

## 4. Match Events Timeline
List in chronological order:
- ⚽ Goals: Player Name (Minute') - Assisted by: [Player if available]
- 🟨 Yellow Cards: Player Name (Minute')
- 🟥 Red Cards: Player Name (Minute')
- 🔄 Substitutions if significant

IMPORTANT:
- Extract data from the provided tables and summaries
- If data is missing, write "Data not available"
- Use clear formatting and be specific with numbers
- Focus on accuracy and completeness"""

        print("\nSending data to Google Gemini API for analysis...")

        try:
            # Ensure text_content is a string
            if not isinstance(text_content, str):
                text_content = str(text_content)

            # Limit content to 50k chars to avoid API limits
            limited_content = text_content[:50000] if len(text_content) > 50000 else text_content

            # Prepare the request for Gemini API
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"{prompt}\n\nMatch Data:\n{limited_content}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.4,
                    "topK": 32,
                    "topP": 1,
                    "maxOutputTokens": 4096,
                }
            }

            response = requests.post(
                self.gemini_api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                # Extract the generated text from Gemini's response
                if 'candidates' in result and len(result['candidates']) > 0:
                    gemini_response = result['candidates'][0]['content']['parts'][0]['text']
                    print("Successfully received response from Gemini API")
                    return gemini_response
                else:
                    print("Unexpected response structure from Gemini API")
                    return None
            else:
                print(f"Gemini API returned status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except Exception as e:
            print(f"Error processing with Gemini API: {str(e)}")
            return None

    def extract_match_data(self, html_content):
        """
        Extract relevant match data from HTML using BeautifulSoup

        Args:
            html_content: The raw HTML content

        Returns:
            A cleaner, more focused text containing just the match data
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')

            extracted_data = []

            # Extract scorebox (match summary)
            scorebox = soup.find('div', {'class': 'scorebox'})
            if scorebox:
                extracted_data.append("=== MATCH SUMMARY ===")
                extracted_data.append(scorebox.get_text(separator='\n', strip=True))
                extracted_data.append("\n")

            # Extract team stats tables
            stats_tables = soup.find_all('table', {'class': 'stats_table'})
            for i, table in enumerate(stats_tables):
                table_id = table.get('id', f'table_{i}')
                extracted_data.append(f"\n=== TABLE: {table_id} ===")

                # Get table headers
                headers = []
                thead = table.find('thead')
                if thead:
                    for th in thead.find_all('th'):
                        headers.append(th.get_text(strip=True))
                    extracted_data.append(" | ".join(headers))
                    extracted_data.append("-" * 80)

                # Get table rows
                tbody = table.find('tbody')
                if tbody:
                    for row in tbody.find_all('tr'):
                        cells = []
                        for cell in row.find_all(['td', 'th']):
                            cells.append(cell.get_text(strip=True))
                        if cells:
                            extracted_data.append(" | ".join(cells))

                extracted_data.append("\n")

            # Extract match events (goals, cards, etc.)
            events = soup.find_all('div', {'class': 'event'})
            if events:
                extracted_data.append("\n=== MATCH EVENTS ===")
                for event in events:
                    extracted_data.append(event.get_text(separator=' ', strip=True))
                extracted_data.append("\n")

            result = "\n".join(extracted_data)
            print(f"Extracted {len(result)} characters of structured match data")

            # Save extracted data for debugging
            with open('debug_extracted_data.txt', 'w', encoding='utf-8') as f:
                f.write(result)
            print("Saved extracted data to debug_extracted_data.txt")

            return result

        except Exception as e:
            print(f"Error extracting match data: {str(e)}")
            print("Falling back to raw HTML")
            return html_content

    def fetch_direct(self, fbref_url):
        """
        Fallback: Try to fetch directly with requests (may not work for all sites)

        Args:
            fbref_url: The FBref match URL to scrape

        Returns:
            The HTML content from the page
        """
        print(f"\nTrying direct fetch as fallback from: {fbref_url}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(fbref_url, headers=headers, timeout=30)

            if response.status_code == 200:
                content = response.text
                print(f"Successfully fetched {len(content)} characters via direct request")

                with open('debug_direct_content.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("Saved direct fetch content to debug_direct_content.html")

                return content
            else:
                print(f"Direct fetch returned status code: {response.status_code}")
                return None

        except Exception as e:
            print(f"Error in direct fetch: {str(e)}")
            return None

    def scrape_and_analyze(self, fbref_url, output_file=None, try_fallback=True):
        """
        Complete workflow: Fetch from FBref using Steel API, then analyze with Gemini

        Args:
            fbref_url: The FBref match URL
            output_file: Optional file to save the results
            try_fallback: Whether to try direct fetch if Steel API fails

        Returns:
            Dictionary containing the results
        """
        # Step 1: Fetch content using Steel API
        raw_content = self.fetch_with_steel_api(fbref_url)

        # Step 1b: Fallback to direct fetch if Steel API fails
        if not raw_content and try_fallback:
            print("\nSteel API fetch failed, trying direct fetch...")
            raw_content = self.fetch_direct(fbref_url)

        if not raw_content:
            print("Failed to fetch content from FBref (tried all methods)")
            return None

        # Step 2: Extract structured match data from HTML
        print("\nExtracting structured match data from HTML...")
        extracted_data = self.extract_match_data(raw_content)

        # Step 3: Process with Gemini API
        gemini_analysis = self.process_with_gemini(extracted_data)

        if not gemini_analysis:
            print("Failed to process content with Gemini API")
            return None

        # Prepare results
        results = {
            "url": fbref_url,
            "timestamp": datetime.now().isoformat(),
            "raw_content_length": len(raw_content),
            "gemini_analysis": gemini_analysis
        }

        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                if output_file.endswith('.json'):
                    json.dump(results, f, indent=2, ensure_ascii=False)
                else:
                    f.write(f"# FBref Match Analysis\n\n")
                    f.write(f"**URL:** {fbref_url}\n")
                    f.write(f"**Timestamp:** {results['timestamp']}\n\n")
                    f.write("## Gemini Analysis\n\n")
                    f.write(gemini_analysis)
            print(f"\nResults saved to: {output_file}")

        return results


def main():
    """
    Main function to run the scraper
    """
    # Example FBref match URL (Champions League Final 2023)
    # You can change this to any FBref match URL
    match_url = "https://fbref.com/en/matches/633d3171/Pafos-FC-Villarreal-November-5-2025-Champions-League"

    # Get Steel API key from environment variable or input
    steel_api_key = os.environ.get('STEEL_API_KEY')

    if not steel_api_key:
        print("Please enter your Steel API key:")
        print("(Get it from: https://app.steel.dev)")
        steel_api_key = input("Steel API Key: ").strip()

    if not steel_api_key:
        print("Error: Steel API key is required!")
        return

    # Get Gemini API key from environment variable or input
    gemini_api_key = os.environ.get('GEMINI_API_KEY')

    if not gemini_api_key:
        print("\nPlease enter your Google Gemini API key:")
        print("(Get it from: https://makersuite.google.com/app/apikey)")
        gemini_api_key = input("Gemini API Key: ").strip()

    if not gemini_api_key:
        print("Error: Gemini API key is required!")
        return

    # Create scraper instance
    scraper = FBrefScraper(steel_api_key, gemini_api_key)

    # Run the scraper
    print("\n" + "=" * 60)
    print("FBref Match Scraper with Steel API + Google Gemini")
    print("=" * 60)
    print()

    results = scraper.scrape_and_analyze(
        fbref_url=match_url,
        output_file="match_analysis.md"
    )

    if results:
        print("\n" + "=" * 60)
        print("GEMINI ANALYSIS RESULT (Copy this for your PR):")
        print("=" * 60)
        print()
        print(results['gemini_analysis'])
        print()
        print("=" * 60)
    else:
        print("\nScraping failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
