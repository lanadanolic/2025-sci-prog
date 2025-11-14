# Vogue Adria Scraper + AI Sažetak

Ovaj projekt dohvaća aktualne vijesti s [VogueAdria.com](https://vogueadria.com), čisti sadržaj i koristi **Google Gemini AI** za automatsko generiranje sažetka i pregleda dana.

---

## Kako radi

1. **Scraper** dohvaća HTML s početne stranice Vogue Adria.
2. **BeautifulSoup** čisti tekstualni sadržaj.
3. **Google Gemini AI** analizira sadržaj i generira:
   - glavne teme u 5 točaka  
   - kratak modno-urednički pregled dana
4. Rezultat se ispisuje u terminalu (ili možeš ga lako spremiti u `.txt` datoteku).

---

## Tehnologije

- [Python 3.10+](https://www.python.org/)
- [Marimo](https://docs.marimo.io/) — interaktivni Python workflow
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [Requests](https://pypi.org/project/requests/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [Google Generative AI](https://ai.google.dev/)

---

## Instalacija

Kloniraj repozitorij i instaliraj potrebne pakete:

```bash
git clone https://github.com/tvoj-username/vogueadria-scraper.git
cd vogueadria-scraper
pip install -r requirements.txt
