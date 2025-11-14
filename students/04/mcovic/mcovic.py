import marimo

__generated_with = "0.17.2"
app = marimo.App()


@app.cell
def _():
    import os
    import sys
    import json
    import textwrap
    from typing import Tuple

    TARGET_URL = sys.argv[1] if len(
        sys.argv) > 1 else "https://www.bbc.com/news"

    def fetch_with_requests(url: str) -> Tuple[str, str]:
        """Simple fallback using requests (public pages only). Returns (html, text)."""
        try:
            import requests
            from bs4 import BeautifulSoup
        except Exception as e:
            raise RuntimeError(
                "requests and bs4 are required for fallback mode. Install via: pip install requests beautifulsoup4") from e

        resp = requests.get(
            url, headers={"User-Agent": "MarimoScraper/1.0 (+https://example)"}, timeout=20)
        resp.raise_for_status()
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        # Extract visible text (simple)
        for script in soup(["script", "style", "noscript"]):
            script.extract()
        text = soup.get_text(separator=" \n ", strip=True)
        # normalize whitespace
        text = "\n".join(line.strip()
                         for line in text.splitlines() if line.strip())
        return html, text

    def fetch_with_steel(url: str) -> Tuple[str, str]:
        """Attempt to use Steel SDK (if available and configured).
        Returns (html, text) -- exact fields depend on your Steel instance.
        This function is intentionally defensive and will raise on misconfiguration.
        """
        try:
            # steel-python SDK: pip install steel-sdk
            from steel import Steel
        except Exception as e:
            raise RuntimeError(
                "steel-sdk not installed. Install it with: pip install steel-sdk") from e

        base_url = os.environ.get("STEEL_BASE_URL", None)
        api_key = os.environ.get("STEEL_API_KEY", None)
        client_kwargs = {}
        if base_url:
            client_kwargs["base_url"] = base_url
        if api_key:
            client_kwargs["api_key"] = api_key

        client = Steel(**client_kwargs)
        # Create a session and navigate - different Steel versions have different helpers.
        # Below we try a common pattern; adjust if your Steel SDK version differs.
        session = client.sessions.create()
        client.sessions.navigate(session.id, url=url, wait_until="networkidle")
        # Try to get HTML
        html = client.sessions.content(session.id, format="html") if hasattr(
            client.sessions, "content") else ""
        # Try to get text
        text = client.sessions.content(session.id, format="text") if hasattr(
            client.sessions, "content") else ""

        # As a fallback, run a simple page.evaluate to get document.body.innerText
        if not text:
            try:
                ev = client.sessions.evaluate(
                    session.id, "() => document.body.innerText")
                text = ev.get("result", "") if isinstance(
                    ev, dict) else str(ev)
            except Exception:
                text = ""

        # close session
        client.sessions.delete(session.id)
        return html or "", text or ""

    def call_google_genai(text: str) -> dict:
        """Call Google Generative AI (Gemini) to summarize and extract structured data.
        This function supports two common Python client styles; pick what matches your environment.
        Make sure GOOGLE_API_KEY is set in the environment.
        Returns a dict with 'summary' and 'structured' fields.
        """
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Please set GOOGLE_API_KEY environment variable (Gemini / Google Generative AI key)")

        # Option A: new google-genai (preferred if installed)
        try:
            import google.genai as genai  # try new namespace first (example)
        except Exception:
            genai = None

        # Option B: older google-generativeai package
        try:
            import google.generativeai as genold
        except Exception:
            genold = None

        prompt = textwrap.dedent(f"""You are an assistant that reads an extracted webpage and produces:
        1) a short 2-3 sentence summary (in Croatian);
        2) a small set of structured facts (as bullet points) that a human could copy into a PR description.
        Provide the output as JSON with keys: summary, structured_text, top_items (list).

        Webpage excerpt (first 2000 chars):
        {text[:2000]}
        """)

        # Try the new `google-genai` interface first
        if genai is not None:
            try:
                client = genai.Client(api_key=api_key)
                model = "models/text-bison-001" if hasattr(
                    genai, "Client") else "gemini-1.5"
                resp = client.generate_text(
                    model=model, prompt=prompt, max_output_tokens=300)
                summary_text = resp.text if hasattr(
                    resp, "text") else str(resp)
                # crude postprocessing: return JSON-like fields
                return {"summary": summary_text, "structured_text": "(see summary)", "top_items": []}
            except Exception as e:
                print(
                    "google-genai client failed, falling back to older client...", file=sys.stderr)

        if genold is not None:
            try:
                genold.configure(api_key=api_key)
                # older client style
                model = genold.GenerativeModel(
                    "gemini-2.5-flash") if hasattr(genold, "GenerativeModel") else None
                if model:
                    resp = model.generate_content(prompt)
                    out = resp.text if hasattr(resp, "text") else str(resp)
                else:
                    # fallback to simple generate
                    resp = genold.generate(prompt)
                    out = getattr(resp, "text", str(resp))
                return {"summary": out, "structured_text": "(see summary)", "top_items": []}
            except Exception as e:
                raise RuntimeError(
                    "Google client calls failed: %s" % (e,)) from e

        # If no client libraries, fallback to the REST approach (not implemented here)
        raise RuntimeError(
            "No supported Google GenAI client library installed (google-genai or google-generativeai). Install one and set GOOGLE_API_KEY.")

    def main():
        url = TARGET_URL
        steel_enabled = bool(os.environ.get("STEEL_API_KEY")
                             or os.environ.get("STEEL_BASE_URL"))

        print("Target URL:", url)
        html, text = "", ""

        if steel_enabled:
            print("Attempting to fetch via Steel...", file=sys.stderr)
            try:
                html, text = fetch_with_steel(url)
            except Exception as e:
                print("Steel fetch failed:", e, file=sys.stderr)
                print("Falling back to requests-based fetch.", file=sys.stderr)
                html, text = fetch_with_requests(url)
        else:
            html, text = fetch_with_requests(url)

        # Print a short excerpt of raw text (for PR)
        excerpt = text[:500]
        print("\n--- RAW TEXT EXCERPT (first ~500 chars) ---\n")
        print(excerpt)
        print("\n--- END RAW EXCERPT ---\n")

        # Call Google AI to summarize / extract
        try:
            analysis = call_google_genai(text)
        except Exception as e:
            print("Google AI call failed:", e, file=sys.stderr)
            analysis = {"summary": "(Google AI call failed: %s)" %
                        e, "structured_text": "", "top_items": []}

        # Print structured output suitable to paste into PR description
        print("\n--- LLM RESULT (copy-paste into PR) ---\n")
        print("Summary (croatian):\n", analysis.get("summary"), "\n")
        print("Structured / bullets:\n", analysis.get("structured_text"))
        print("Top items list:\n", json.dumps(analysis.get(
            "top_items", []), indent=2, ensure_ascii=False))
        print("\n--- END LLM RESULT ---\n")

    def _main_():
        main()

    _main_()
    return


if __name__ == "__main__":
    app.run()
