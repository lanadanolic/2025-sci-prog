import marimo

_generated_with_ = "0.16.5"
app = marimo.App()

# ucitavanje API kljuceva


@app.cell
def get_api_keys():
    import os
    from dotenv import load_dotenv

    # ucitaj iz .env datoteke ako postoji
    load_dotenv()

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("postavi GOOGLE_API_KEY")

    print("google API key uspjesno ucitan")
    return GOOGLE_API_KEY


end = None


# dohvat i ciscenje sadrzaja s VogueAdria.com
@app.cell
def scrape_vogue_adria():
    import requests
    from bs4 import BeautifulSoup

    url = "https://vogueadria.com/"
    print(f"dohvacam podatke sa: {url}")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"neuspjesan dohvat: {e}")

    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    # preferiraj <main>, fallback na cijeli dokument
    main = soup.find("main") or soup

    # izdvoji tekstualni sadržaj bez HTML tagova
    text = main.get_text(separator=" ", strip=True)
    clean_text = " ".join(text.split())

    print("uspjesno dohvacen sadrzaj:\n")
    print(clean_text[:500])
    return url, clean_text


end = None


# analiza sadrzaja pomocu Google Gemini
@app.cell
def analyze_news(GOOGLE_API_KEY, clean_text):
    import google.generativeai as genai

    # konfiguracija API kljuca
    genai.configure(api_key=GOOGLE_API_KEY)

    # prompt za AI model
    prompt = f"""
    Ovo je tekst s naslovne stranice Vogue Adria:
    {clean_text[:2500]}

    ➤ Sažmi glavne teme/vijesti u 5 točaka.
    ➤ Napiši kratak pregled dana (1–2 rečenice) u stilu modnog urednika.
    ➤ Odgovor napiši na gramatički ispravnom hrvatskom jeziku.
    """

    try:
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        result = model.generate_content(prompt)
        summary = result.text
        print("\nAI sazetak vijesti:\n")
        print(summary)
    except Exception as e:
        summary = f"greska kod Gemini API poziva: {e}"

    return summary


end = None


# ispis rezultata u terminal
@app.cell
def show_results(url, clean_text, summary):
    print("=" * 70)
    print(f"VOGUE ADRIA SCRAPER")
    print("=" * 70)
    print(f"URL: {url}\n")
    print(f"isjecak teksta:\n{clean_text[:400]}...\n")
    print("sazetak vijesti:\n")
    print(summary)
    print("=" * 70)


end = None


# pokretanje aplikacije
if __name__ == "__main__":
    app.run()
