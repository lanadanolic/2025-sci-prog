
import marimo as mo

app = mo.App()


@app.cell
def __():
    import os
    import requests
    from dotenv import load_dotenv
    import google.generativeai as genai
    from bs4 import BeautifulSoup
    import json
    import marimo as mo
    from pathlib import Path
    return os, requests, load_dotenv, genai, BeautifulSoup, json, mo, Path


@app.cell
def __(mo):
    mo.md("# 🔑 API Keys Configuration")
    return


@app.cell
def __(load_dotenv, os, mo, Path):
    load_dotenv()
    try:
        load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)
    except Exception:
        pass
    
    steel_default = os.getenv("STEEL_API_KEY", "")
    google_default = os.getenv("GOOGLE_API_KEY", "")
    
    steel_input = mo.ui.text(
        label="Steel API Key",
        placeholder="ste-.",
        value=steel_default,
        kind="password"
    )
    
    google_input = mo.ui.text(
        label="Google AI API Key",
        placeholder="AIzaSy.",
        value=google_default,
        kind="password"
    )
    
    mo.vstack([
        mo.md("Enter your API keys (or they will be loaded from .env)"),
        steel_input,
        google_input
    ])
    return steel_input, google_input


@app.cell
def __(mo):
    mo.md("---\n\n# 📰 Scraper Configuration")
    return


@app.cell
def __(mo):
    run_btn = mo.ui.run_button(label="Scrape & Summarize Ars Technica")
    run_btn
    return run_btn,


@app.cell
def __(genai, requests, run_btn, steel_input, google_input, mo, BeautifulSoup, json):
    
    def steel_fetch_text(url: str, api_key: str) -> str:
        if not api_key:
            return "ERROR: STEEL_API_KEY is not set."
        try:
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

    def gemini_summarize(text: str, api_key: str) -> str:
        if not api_key:
            return "ERROR: GOOGLE_API_KEY is not set."
        try:
            genai.configure(api_key=api_key)
            
            # Dynamically find a model that supports generateContent
            try:
                models = list(genai.list_models())
            except Exception:
                models = []
            candidate_models = []
            for m in models:
                try:
                    methods = getattr(
                        m, "supported_generation_methods", []) or []
                    if "generateContent" in methods:
                        candidate_models.append(getattr(m, "name", ""))
                except Exception:
                    continue
            
            # Ensure some reasonable defaults at the end
            candidate_models += [
                "gemini-1.5-flash",
                "gemini-pro",
            ]

            prompt = f"Summarize the following tech news article into a concise overview: {text[:8000]}"

            last_err = None
            for model_name in candidate_models:
                try:
                    if not model_name:
                        continue
                    model = genai.GenerativeModel(model_name)
                    resp = model.generate_content(prompt)
                    text_result = getattr(
                        resp, "text", "") or "(empty response)"
                    return text_result
                except Exception as inner_e:
                    last_err = inner_e
                    continue
            if last_err is not None:
                return f"ERROR from Gemini: {last_err}"
            return "(empty response)"
        except Exception as e:
            return f"ERROR from Gemini: {e}"

    view = mo.md("Click 'Scrape & Summarize Ars Technica' to start.")

    if run_btn.value:
        steel_key = steel_input.value.strip()
        google_key = google_input.value.strip()
        
        if not steel_key or not google_key:
            view = mo.md("❌ Missing API keys! Please enter both API keys above.")
        else:
            view = mo.md("⏳ Fetching RSS feed...")
            
            articles_to_process = []
            feed_url = "https://arstechnica.com/feed/"
            try:
                response = requests.get(feed_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'lxml-xml')
                for item in soup.select("item")[:10]:
                    title = item.find("title").text
                    link = item.find("link").text
                    articles_to_process.append({'title': title, 'link': link})
            except Exception as e:
                view = mo.md(f"❌ An error occurred while scraping the RSS feed: {e}")

            if articles_to_process:
                results = []
                for article_info in articles_to_process:
                    results.append(mo.md(f"⏳ Scraping: {article_info['title']}..."))
                    article_text = steel_fetch_text(article_info['link'], steel_key)
                    
                    if article_text.startswith("ERROR"):
                        results.append(mo.md(f"❌ Error scraping {article_info['link']}: {article_text}"))
                    else:
                        results.append(mo.md(f"Summarizing: {article_info['title']}..."))
                        summary = gemini_summarize(article_text, google_key)
                        if summary.startswith("ERROR"):
                            results.append(mo.md(f"❌ Error summarizing {article_info['title']}: {summary}"))
                        else:
                            results.append(mo.md(f"### {article_info['title']}\n\n{summary}"))
                view = mo.vstack(results)

    view
    return view, steel_fetch_text, gemini_summarize