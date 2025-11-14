# Njuškalo iPhone 17 Scraper 📱

 Ovaj scraper koristi **Steel API** za preuzimanje 5 najjeftinijih oglasa sa Njuškala koji sadrže "iPhone 17" u naslovu i **Google Gemini API** za generiranje detaljnih sažetaka.

---

## 🔍 Koji URL scrapamo i zašto

**URL:**  
[https://www.njuskalo.hr/search/?keywords=iphone+17&price[min]=500&price[max]=1500&sort=cheap](https://www.njuskalo.hr/search/?keywords=iphone+17&price[min]=500&price[max]=1500&sort=cheap)

**Razlog:**
- Scrapamo pretragu za iPhone 17 uređaje u cjenovnom rangu 500-1500 EUR  
- Sortiranje po cijeni (`sort=cheap`) osigurava da dobijemo najjeftinije oglase prvo  
- Izvlačimo top 5 najjeftinijih ponuda sa detaljima (cijena, stanje, lokacija)

---

## ✅ Funkcionalnosti
- Scraping top 5 najjeftinijih iPhone 17 oglasa  
- Ekstrakcija podataka: naslov, cijena, stanje (novo/rabljeno), opis, link  
- AI generiranje detaljnih sažetaka za svaki oglas (Gemini)  
- Klasifikacija stanja uređaja (Novo/Rabljeno/Nije navedeno)  
- Export rezultata u **JSON** i **TXT** format  
- Formatiran PR output

## Kako pokrenuti:

1. Kreiraj `.env` datoteku unutar `./students/04/exercise/smachiedo/` i dodaj Steel i Google Gemini API ključeve:
```env
STEEL_API_KEY=ovdje_upisi_steel_key
GOOGLE_API_KEY=ovdje_upisi_google_key
```


2. Izvrši sljedeću naredbu: 
```env
marimo run ./students/04/exercise/smachiedo/scraper.py
```