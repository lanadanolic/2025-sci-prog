import marimo

__generated_with = "0.17.7"
app = marimo.App()


@app.cell
def get_api_keys():
    import os
    from dotenv import load_dotenv

    env_path = os.path.join(os.getcwd(), '.env')
    print("Looking for .env at:", env_path)

    load_dotenv(dotenv_path=env_path)

    GOOGLE_API_KEY = os.getenv("GOOGLE_API")
    if not GOOGLE_API_KEY:
        raise ValueError("postavi GOOGLE_API_KEY u .env datoteku")
    print("✅ Google API key uspješno učitan.")
    return (GOOGLE_API_KEY,)


@app.cell
def scrape_bbc():
    import requests
    from bs4 import BeautifulSoup

    url = "https://www.bbc.com/news"
    print(f"Dohvaćam sadržaj s: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    }

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # pronalazak naslova vijesti
    headlines = [h.get_text(strip=True) for h in soup.find_all("h2")[:10]]
    text = " ".join(headlines)
    clean_text = " ".join(text.split())

    print("✅ Uspješno dohvaćen sadržaj:\n")
    print(clean_text[:400])
    return (clean_text,)


@app.cell
def analyze_news(GOOGLE_API_KEY, clean_text):
    import google.generativeai as genai

    genai.configure(api_key=GOOGLE_API_KEY)

    prompt = f"""
    Ovo su naslovi s BBC News portala:
    {clean_text[:2000]}

    ➤ Sažmi glavne vijesti u 5 točaka.
    ➤ Napiši kratki pregled dana (1–2 rečenice) u novinarskom tonu.
    ➤ Odgovor napiši na hrvatskom jeziku.
    """

    try:
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        result = model.generate_content(prompt)
        summary = result.text
        print("\n🧾 AI Sažetak vijesti:\n")
        print(summary)
    except Exception as e:
        summary = f"Greška u pozivu Google AI API-ja: {e}"
    return


if __name__ == "__main__":
    app.run()
