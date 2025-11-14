## Jutarnji.hr Scraper

Ova aplikacija dohvaća sadržaj s naslovne stranice [Jutarnji.hr](https://www.jutarnji.hr/)  
i pomoću **Google Gemini AI** modela generira sažetak glavnih vijesti u 5 točaka.

### Tehnologije:
- **Marimo** — interaktivno Python okruženje  
- **Requests + BeautifulSoup** — dohvat i parsiranje HTML-a  
- **Google Generative AI (Gemini)** — analiza i sažetak teksta  

### Pokretanje:
1. Instaliraj potrebne pakete:
   ```bash
   pip install marimo requests beautifulsoup4 google-generativeai python-dotenv
