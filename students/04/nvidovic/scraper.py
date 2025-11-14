import marimo

__generated_with = "0.17.7"
app = marimo.App()


@app.cell
def _():
    import os
    import requests
    from dotenv import load_dotenv
    import google.generativeai as genai
    return genai, load_dotenv, os, requests


@app.cell
def _(load_dotenv, os):
    import marimo as _mo

    from pathlib import Path
    load_dotenv()
    try:
        load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)
    except Exception:
        pass

    steel_api_key = os.getenv("STEEL_API_KEY", "")
    google_api_key = os.getenv("GOOGLE_API_KEY", "")
    return google_api_key, steel_api_key


@app.cell
def _():
    import marimo as _mo

    url_input = _mo.ui.text(
        label="URL",
        placeholder="URL",
        value="https://www.index.hr"
    )
    run_btn = _mo.ui.run_button(label="Scrape and Analyze Index.hr")
    _mo.hstack([url_input, run_btn])
    return run_btn, url_input


@app.cell
def _(genai, google_api_key, requests, run_btn, steel_api_key, url_input):
    import marimo as _mo

    def steel_fetch_text(url: str, api_key: str) -> str:
        if not api_key:
            return "ERROR: STEEL_API_KEY nije postavljen."
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

    def gemini_analyze_index_hr(text: str, api_key: str) -> str:
        if not api_key:
            return "ERROR: GOOGLE_API_KEY nije postavljen."
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            prompt = (
                "Analiziraj sljedeći tekst sa naslovne stranice index.hr i izvuci TOP 5 najvažnijih vijesti.\n\n"
                "Za svaku vijest navedi:\n"
                "- Naslov vijesti\n"
                "- Kratki opis (1 rečenica) o čemu se radi\n\n"
                "Na kraju napiši sažetak (2-3 rečenice): koje su glavne teme danas na index.hr?\n\n"
                "Formatiraj odgovor kao listu s bullet točkama na hrvatskom jeziku.\n\n"
                "Nemoj koristiti JSON ili code blokove, samo čisti tekst.\n\n"
                f"Tekst:\n{text[:8000]}"
            )

            resp = model.generate_content(prompt)
            return resp.text
        except Exception as e:
            return f"ERROR from Gemini: {e}"

    view = _mo.md(
        "Kliknite 'Scrape and Analyze Index.hr' za analizu naslovne stranice.")

    if run_btn.value:
 
        url = (url_input.value or "").strip()
        if not url:
            view = _mo.md("ERROR: URL nije unesen.")
        elif not steel_api_key or not google_api_key:
            view = _mo.md(f"❌ Missing API keys!\n\nSteel key present: {bool(steel_api_key)}\n\nGoogle key present: {bool(google_api_key)}")
        else:
            steel_text = steel_fetch_text(url, steel_api_key)

            if not isinstance(steel_text, str):
                steel_text = str(steel_text)

            if steel_text.startswith("ERROR"):
                view = _mo.md(f"❌ {steel_text}")
            else:
                excerpt = (steel_text or "").strip()[:800]

                llm_out = gemini_analyze_index_hr(
                    steel_text, google_api_key) if steel_text else "(nema teksta)"

                results_text = (
                    f"# 📰 Index.hr Scraper Rezultati\n\n"
                    f"**Scraped URL:** `{url}`\n\n"
                    f"---\n\n"
                    f"## Steel Output (isječak, prvih 800 znakova)\n\n"
                    f"```\n{excerpt}\n```\n\n"
                    f"---\n\n"
                    f"## 🤖 LLM Analiza (Google AI)\n\n"
                    f"{llm_out}\n\n"
                    f"---\n\n"
                    f"*Duljina ukupnog teksta: {len(steel_text)} znakova*"
                )

                download_btn = _mo.download(
                    data=results_text.encode('utf-8'),
                    filename="index_hr_results.md",
                    mimetype="text/markdown",
                    label="⬇️ Download Results as Markdown"
                )

                view = _mo.vstack([
                    _mo.md(results_text),
                    download_btn
                ])

    view
    return


if __name__ == "__main__":
    app.run()
