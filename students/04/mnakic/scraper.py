import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import requests
    from dotenv import load_dotenv  # potrebno instalirati
    import google.generativeai as genai
    return genai, load_dotenv, os, requests


@app.cell
def _(load_dotenv, os):
    load_dotenv()

    STEEL_API_KEY = os.getenv("STEEL_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    return GOOGLE_API_KEY, STEEL_API_KEY


@app.cell
def _(GOOGLE_API_KEY, STEEL_API_KEY):
    import marimo as _mo

    steel_input = _mo.ui.text(
        label="Steel API",
        value=STEEL_API_KEY or "",
        kind="password"
    )

    google_input = _mo.ui.text(
        label="Google AI API",
        value=GOOGLE_API_KEY or "",
        kind="password"
    )

    form = _mo.vstack([
        _mo.md("Unesi svoje API ključeve:"),
        steel_input,
        google_input
    ])

    form
    return google_input, steel_input


@app.cell
def _(GOOGLE_API_KEY, STEEL_API_KEY, google_input, steel_input):
    current_steel_key = steel_input.value or STEEL_API_KEY
    current_google_key = google_input.value or GOOGLE_API_KEY

    url = "https://hidra.hr/o-hidri/"
    steel_url = "https://api.steel.dev/v1/scrape"

    print(current_steel_key)
    return current_google_key, url


@app.cell
def _(requests, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        page_content = ""

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Direktno uzmi HTML sadržaj
        page_content = response.text

    except Exception as e:
        print(f"Error: {str(e)}")
        page_content = ""
    return page_content, response


@app.cell
def _(page_content):
    print(page_content)
    return


@app.cell
def _(current_google_key, genai, page_content, response):
    genai.configure(api_key=current_google_key)

    if page_content:
        model = genai.GenerativeModel("gemini-1.5-pro")

        ai_response = model.generate_content(
            f"Analiziraj sljedeći sadržaj web stranice i navedi sve proizvode koji postoje: {page_content}"
        )

        print(response.text)
    else:
        print("Nema sadržaja za analizu.")

    return


if __name__ == "__main__":
    app.run()
