import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import os
    import requests
    import google.generativeai as genai
    return genai, os, requests


@app.cell
def _():
    url = "https://www.index.hr/vijesti"
    return (url,)


@app.cell
def _(os):
    STEEL_API_KEY = os.environ.get("STEEL_API_KEY")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    return GEMINI_API_KEY, STEEL_API_KEY


@app.cell
def _(STEEL_API_KEY, requests, url):
    def scrape():
        if not STEEL_API_KEY:
            return "STEEL_API_KEY nije postavljen!"

        STEEL_ENDPOINT = "https://api.steel.dev/v1/scrape"
        try:
            response = requests.post(
                STEEL_ENDPOINT,
                headers={
                    "steel-api-key": STEEL_API_KEY,
                    "content-type": "application/json",
                    "accept": "application/json",
                },
                json={
                    "url": url,
                    "extract": "text",
                    "useProxy": False,
                    "delay": 1,
                    "fullPage": True,
                    "region": "",
                },
                timeout=30
            )

            print("Status code:", response.status_code)

            try:
                data = response.json()
                scraped_text = data.get("content", {}).get("html", "")
                print(scraped_text[:500])
                if scraped_text:
                    return scraped_text
            except ValueError:
                return response.text

        except Exception as e:
            return f"Greška: {e}"

    scraped_content = scrape()
    return (scraped_content,)


@app.cell
def _(GEMINI_API_KEY, genai, scraped_content):
    def analyze(text_to_analyze):
        snippet = str(text_to_analyze)[:200000]
        genai.configure(api_key=GEMINI_API_KEY)

        prompt_content = "Analyze the provided content from the Croatian news portal Index.hr/vijesti. \
                          Identify the top 5 most important current **Croatian/Regional** news headlines and their subheadings/summaries. \
                          Format the final result as a clear Markdown table with columns 'Naslov' and 'Sažetak'. \
                          The entire response must be in **Croatian** language. Do not use Markdown-specific characters such as asterisks and escape characters."

        system_instruction = [
            f"Provided content snippet from Index.hr/vijesti: {snippet}",
            "You are a concise, professional Croatian news analyst and editor. \
             Your only job is to extract, summarize, and present the most critical Croatian and regional events. \
             Start your response with: 'TOP DOMAĆE VIJESTI:'"
        ]

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )

        try:
            ai_response = model.generate_content(prompt_content)
            return ai_response.text

        except Exception as e:
            return f"Geimini erroru: {e}"

    gemini_analysis = analyze(scraped_content)
    return (gemini_analysis,)


@app.cell
def _(gemini_analysis):
    print(gemini_analysis)
    return


if __name__ == "__main__":
    app.run()
