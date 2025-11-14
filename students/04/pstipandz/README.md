# Web Scraper za Index.hr Vijesti

## Pregled
Ovaj projekt scrapa Index.hr vijesti i koristi Google Gemini AI za izvlačenje top 5 najvažnijih trenutnih vijesti.

## Zašto Index.hr?
Index.hr je odabran jer:
- Vodeći hrvatski news portal s ažurnim vijestima
- Sadrži raznolike vijesti (politika, ekonomija, svijet)

## Instalacija

1. **Instalirajte pakete:**
```bash
   pip install marimo requests google-generativeai
```

2. **Postavite environment varijable:**

   **Linux/Mac:**
```bash
   export STEEL_API_KEY="vaš_steel_api_ključ"
   export GEMINI_API_KEY="vaš_gemini_api_ključ"
```

   **Windows (PowerShell):**
```powershell
   $env:STEEL_API_KEY="vaš_steel_api_ključ"
   $env:GEMINI_API_KEY="vaš_gemini_api_ključ"
```

## Gdje nabaviti API ključeve
### Steel API ključ
1. Posjetite [Steel.dev](https://steel.dev/)
2. Registrirajte se za account
3. Kreirajte novi API ključ

### Google Gemini API ključ
1. Posjetite [Google AI Studio](https://aistudio.google.com/app/api-keys)
2. Prijavite se s Google accountom
3. Kreirajte novi API ključ

## Pokretanje

1. **Pokrenite Marimo notebook:**
```bash
   marimo edit vjezba04.py
```

2. **Ili pokrenite kao aplikaciju:**
```bash
   marimo run vjezba04.py
```