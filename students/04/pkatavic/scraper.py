import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import requests
    from pathlib import Path
    from dotenv import load_dotenv

    script_folder = Path(__file__).parent
    dotenv_path = script_folder / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    STEEL_API_KEY = os.getenv("STEEL_API_KEY")

    url = "https://www.bbc.com/news"

    endpoint = "https://api.steel.dev/v1/scrape"

    payload = {
        "url": url,
        "format": ["html"],
        "screenshot": False,
        "pdf": False,
        "delay": 1,
        "useProxy": False,
        "region": ""
    }

    headers = {
        "Content-Type": "application/json",
        "steel-api-key": STEEL_API_KEY
    }

    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        raw_html = data["content"]["html"]
    else:
        print(response.text)
    return os, raw_html


@app.cell
def _(raw_html):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(raw_html, "html.parser")

    # Get all the content - BBC's structure varies
    news_content = soup.find("body")
    
    # Debug: print available classes and ids to see what's actually there
    print("Available main tags:", [tag.name for tag in soup.find_all(['main', 'article', 'section'])[:5]])
    print("Sample divs with classes:", [(div.get('class'), div.get('id')) for div in soup.find_all('div', limit=10)])

    if not(news_content):
        print("Not found")
        news_content = str(soup)  # Fallback to entire HTML
    return (news_content,)


@app.cell
def _(news_content, os):
    from google import genai
    from google.genai import types

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    client = genai.Client()
    ai_response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=[
                str(news_content), 
                "You are a super obsessed, frantic and fixated news enthusiast \
                who talks like they had too many energy drinks."
            ]
        ),
        contents="Tell me the most interesting facts \
        regarding the current top 10 news stories on BBC News \
        based on the provided data. \
        Do not use Markdown-specific characters such \
        as asterisks and escape characters."
    )

    print(ai_response.text)
    return


if __name__ == "__main__":
    app.run()