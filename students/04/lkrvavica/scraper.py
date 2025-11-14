import marimo

__generated_with = "0.16.5"
app = marimo.App()


@app.cell
def _():
    import requests
    from bs4 import BeautifulSoup
    from google import generativeai as genai
    import os
    from dotenv import load_dotenv
    import time

    # Load .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path, override=True)

    # Environment variables
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    # URL to scrape
    url = "https://meteo.hr"

    # Fetch content
    print("→ Dohvaćam sadržaj...")
    try:
        resp = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        resp.raise_for_status()
        html_text = resp.text
        print("✓ Direktan fetch uspješan")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Fetch neuspješan: {e}")
    
    print("SIROVI HTML SADRŽAJ (prvih 1000 znakova)")
    print(html_text[:1000])

    # Parse HTML
    soup = BeautifulSoup(html_text, "html.parser")
    text = soup.get_text(separator=" ")
    clean_text = " ".join(text.split())

    print("SIROVI TEKST (prvih 1000 znakova)")
    print(clean_text[:1000])

    # Prepare prompt
    prompt = f"""
    Ovo je službena vremenska prognoza sa stranice {url}:
    {clean_text[:1500]}

    Napiši kratku, razumljivu i prijateljsku verziju vremenske prognoze
    na hrvatskom jeziku, kao da si radijski voditelj.
    Uključi glavne informacije (vrijeme, temperatura, vjetar, oborine),
    ali nemoj biti previše tehnički.
    """

    # Configure Gemini
    genai.configure(api_key=GOOGLE_API_KEY)

    # Try multiple models in order (skip the ones that hit quota)
    models_to_try = [
        "models/gemini-2.0-flash",          # Najnoviji flash model
        "models/gemini-2.0-flash-exp",      # Experimental verzija
        "models/gemini-flash-latest",       # Alias za najnoviji
        "models/gemini-2.5-flash",          # Stariji ali stabilan
        "models/gemini-2.0-flash-lite",     # Lite verzija (manja kvota)
    ]

    summary = None
    used_model = None

    for model_name in models_to_try:
        try:
            print(f"\n→ Pokušavam model: {model_name}")
            model = genai.GenerativeModel(model_name)
        
            response = model.generate_content(prompt)
            summary = response.text
            used_model = model_name
            print(f"✓ Uspješno s modelom: {model_name}")
            break
        
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"  ⚠️ Kvota prekoračena za {model_name}")
            else:
                print(f"  ✗ Greška: {e}")
            continue

    # If all models failed due to quota, wait and retry
    if not summary:
        print("\n⏳ Svi modeli su prekoračili kvotu. Čekam 45 sekundi...")
        time.sleep(45)
    
        print("\n→ Retry s gemini-2.0-flash...")
        try:
            model = genai.GenerativeModel("models/gemini-2.0-flash")
            response = model.generate_content(prompt)
            summary = response.text
            used_model = "models/gemini-2.0-flash"
            print("✓ Uspjeh nakon čekanja!")
        except Exception as e:
            print(f"✗ Još uvijek ne radi: {e}")

    # Output
    print("\n" + "="*60)
    if summary:
        print("VREMENSKA PROGNOZA")
        print("="*60)
        print(f"(Model: {used_model})\n")
        print(summary)
    else:
        print("GREŠKA - Prekoračena kvota")

    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
