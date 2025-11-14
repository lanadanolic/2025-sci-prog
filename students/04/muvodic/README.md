# Simple Web Scraper (Steel + Google AI)

## Koji URL i zašto
 Scrape-an je url: https://docker-curriculum.com/
 Tu se nalazi detaljni početni tutorijal i uvod u alat Docker. Odlucila sam obradivati ovaj url kako bi imala skracenu verziju (vrlo korisne) stranice i detaljan road map (plan ucenja) koji se moze koristiti tijekom ucenja

## Prije pokretanja

1. Instalirati dependencies i dodati API kljuceve u .env datoteku
   python3 -m pip install --user marimo requests google-generativeai python-dotenv

   *Potrebni API kljucevi**
   STEEL_API_KEY=
   GEMINI_API_KEY=


## Kako pokrenuti

- u terminalu pokrenuti naredbom (ako se nalazite u direktoriju 2025-sci-prog) marimo run students/04/exercise/muvodic/scraper.py

## Izlaz

- Upotrebljeni URL
- Dio teksta koji vrati STEEL
- Opis obradene stranice koja je tutorijal za Docker i road map za pocetnike

