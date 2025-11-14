import marimo

__generated_with = "0.16.5"
app = marimo.App()


@app.cell
def _():
    import os
    import requests
    from dotenv import load_dotenv
    return load_dotenv, os, requests


@app.cell
def _():
    import marimo as _mo

    url_input = _mo.ui.text(value="https://docker-curriculum.com/",disabled=True)
    run_btn = _mo.ui.run_button(label="Click to summarize")
    _mo.hstack([url_input, run_btn])
    return run_btn, url_input


@app.cell
def _(load_dotenv, os, requests):
    import marimo as _mo
    from pathlib import Path
    load_dotenv()

    try:
        load_dotenv(dotenv_path=Path(
            __file__).with_name(".env"), override=False)
    except Exception:
        pass
    steel_key = os.getenv("STEEL_API_KEY")
    google_key = os.getenv("GEMINI_API_KEY")

    def steel_fetch_text(url: str, api_key: str) -> str:
        if not api_key:
            return "ERROR: STEEL_API_KEY nije postavljen (.env)."
        try:
            import json
            from bs4 import BeautifulSoup

            resp = requests.post(
                "https://api.steel.dev/v1/scrape",
                headers={
                    "steel-api-key": api_key,
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
            )
            ct = resp.headers.get("content-type", "")
            if "application/json" in ct:
                data = resp.json()
                if isinstance(data, dict):
                    for key in ("text", "content", "extracted_text"):
                        val = data.get(key)
                        if isinstance(val, str) and val.strip():
                            return val
                    content = data.get("content")
                    if isinstance(content, dict):
                        html = content.get("html") or content.get("body")
                        if isinstance(html, str) and html.strip():
                            soup = BeautifulSoup(html, "html.parser")
                            return soup.get_text(" ", strip=True)
                    html = data.get("html")
                    if isinstance(html, str) and html.strip():
                        soup = BeautifulSoup(html, "html.parser")
                        return soup.get_text(" ", strip=True)
                    return json.dumps(data, ensure_ascii=False)
                if isinstance(data, list):
                    return "\n".join(str(item) for item in data)
                return str(data)
            return resp.text
        except Exception as e:
            return f"ERROR contacting Steel: {e}"
    return google_key, steel_fetch_text, steel_key


@app.cell
def _():
    # corrected gemini_summarize
    from google import genai
    from google.genai import types

    def gemini_summarize(excerpt: str, api_key: str) -> str:

        client = genai.Client(api_key=api_key)

        user_prompt = (
            "You are provided with the results of a web scraping operation. "
            "Summarize the main points and key information from the following excerpt "
            "and give a detailed step-by-step learning plan that can be used as a roadmap "
            "for someone learning Docker:\n\n"
            f"{excerpt}"
        )

        cfg = types.GenerateContentConfig(
            system_instruction=(
                "You are explaining the contents and concepts in the given article to a "
                "complete beginner in the field. Go into depth and provide examples where possible."
            ),
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=cfg,
        )

        return response.text
    return (gemini_summarize,)


@app.cell
def _(
    gemini_summarize,
    google_key,
    run_btn,
    steel_fetch_text,
    steel_key,
    url_input,
):
    import marimo as _mo

    view = _mo.md("Click to scrape")
    if run_btn.value:
        url = (url_input.value).strip()
        if not steel_key or not google_key:
            view = _mo.md("Missing STEEL_API_KEY or GEMINI_API_KEY in .env")
        else:
            steel_text = steel_fetch_text(url, steel_key)
            if not isinstance(steel_text, str):
                steel_text = str(steel_text)
            excerpt = (steel_text or "").strip().replace("\n", " ")[:500]
            llm_out = gemini_summarize(
                excerpt, google_key) if excerpt else "(nema teksta)"
            view = _mo.md(
                f"**Scraped URL:** {url}\n\n"
                f"**Steel output (isječak, ~500 znakova):**\n\n{excerpt}\n\n"
                f"**LLM rezultat:**\n\n{llm_out}"
            )

    view
    return


if __name__ == "__main__":
    app.run()
