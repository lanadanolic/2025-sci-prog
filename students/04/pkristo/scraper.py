import marimo

__generated_with__ = "0.16.5"
app = marimo.App()

# === 1. Učitavanje API ključeva ===
@app.cell
def get_api_keys():
    import os
    from dotenv import load_dotenv

    # Učitaj iz .env datoteke ako postoji
    load_dotenv()

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("❌ Postavi GOOGLE_API_KEY u .env datoteku!")

    print("🔑 Google API ključ uspješno učitan.")
    return GOOGLE_API_KEY
end = None


# === 2. Dohvat i čišćenje sadržaja s Jutarnji.hr ===
@app.cell
def scrape_jutarnji():
    import requests
    from bs4 import BeautifulSoup

    url = "https://www.jutarnji.hr/"
    print(f"🌍 Dohvaćam podatke sa: {url}")

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"⚠️ Neuspješan dohvat: {e}")

    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    # Izdvoji tekstualni sadržaj bez HTML tagova
    text = soup.get_text(separator=" ", strip=True)
    clean_text = " ".join(text.split())

    print("✅ Uspješno dohvaćen sadržaj (isječak):\n")
    print(clean_text[:500])
    return url, clean_text
end = None


# === 3. Analiza sadržaja pomoću Google Gemini ===
@app.cell
def analyze_news(GOOGLE_API_KEY, clean_text):
    import google.generativeai as genai

    # Konfiguracija API ključa
    genai.configure(api_key=GOOGLE_API_KEY)

    # Prompt za AI model
    prompt = f"""
    Ovo je tekst s naslovne stranice Jutarnjeg lista:
    {clean_text[:2500]}

    ➤ Sažmi glavne vijesti u 5 točaka.
    ➤ Napiši kratak pregled dana (1-2 rečenice) u stilu novinskog urednika.
    ➤ Odgovor napiši na hrvatskom jeziku.
    """

    try:
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        result = model.generate_content(prompt)
        summary = result.text
        print("\n🧠 AI Sažetak vijesti:\n")
        print(summary)
    except Exception as e:
        summary = f"⚠️ Greška kod Gemini API poziva: {e}"

    return summary
end = None


# === 4. Ispis rezultata u terminal ===
@app.cell
def show_results(url, clean_text, summary):
    print("=" * 70)
    print(f"📰 JUTARNJI LIST SCRAPER")
    print("=" * 70)
    print(f"URL: {url}\n")
    print(f"Isječak teksta:\n{clean_text[:400]}...\n")
    print("📋 Sažetak vijesti:\n")
    print(summary)
    print("=" * 70)
end = None


# === 5. Pokretanje aplikacije ===
if __name__ == "__main__":
    app.run()
