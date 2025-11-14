import marimo

__generated_with = "0.17.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import requests
    import json
    import os
    import re
    from datetime import datetime
    from dotenv import load_dotenv
    from bs4 import BeautifulSoup

    # Učitaj environment varijable
    load_dotenv('/students/04/exercise/smachiedo/.env')

    STEEL_API_KEY = os.getenv('STEEL_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

    if not STEEL_API_KEY or not GOOGLE_API_KEY:
        raise ValueError("STEEL_API_KEY i GOOGLE_API_KEY moraju biti postavljeni u .env file!")

    SCRAPED_URL = "https://www.njuskalo.hr/search/?keywords=iphone+17&price[min]=500&price[max]=1500&sort=cheap"

    def scrape_njuskalo():
        """Scrape top 5 najjeftinijih iPhone 17 oglasa sa Njuškala"""
    
        scrape_url = "https://api.steel.dev/v1/scrape"
    
        headers = {
            "Steel-Api-Key": STEEL_API_KEY,
            "Content-Type": "application/json"
        }
    
        payload = {
            "url": SCRAPED_URL,
            "waitFor": 5000
        }
    
        try:
            print(f"Scraping {SCRAPED_URL}...")
            response = requests.post(scrape_url, json=payload, headers=headers)
            response.raise_for_status()
        
            result = response.json()
            html_content = result.get('content', {}).get('html', '')
        
            if not html_content:
                print("WARNING: Nema HTML sadržaja!")
                return []
        
            soup = BeautifulSoup(html_content, 'html.parser')
        
            ads = []
            seen_titles = set()
        
            # Traži kontejnere oglasa
            ad_containers = (
                soup.find_all('article') or
                soup.find_all('li', class_=lambda x: x and 'entity' in str(x).lower()) or
                soup.find_all('div', class_=lambda x: x and 'ad' in str(x).lower()) or
                soup.find_all('div', class_=lambda x: x and 'list-item' in str(x).lower())
            )
        
            print(f"Pronađeno {len(ad_containers)} kontejnera oglasa")
        
            for container in ad_containers:
                # Traži naslov
                title_elem = (
                    container.find(['h3', 'h2', 'h4', 'a'], class_=lambda x: x and 'title' in str(x).lower()) or
                    container.find('a', attrs={'data-title': True}) or
                    container.find(['h3', 'h2', 'h4'])
                )
            
                if not title_elem:
                    continue
            
                title = title_elem.get_text().strip()
            
                # Provjeri da li naslov sadrži "iphone 17"
                if not re.search(r'iphone\s*17', title, re.IGNORECASE):
                    continue
            
                # Traži cijenu
                price_elem = (
                    container.find('span', class_=lambda x: x and 'price' in str(x).lower()) or
                    container.find('strong', class_=lambda x: x and 'price' in str(x).lower()) or
                    container.find(string=re.compile(r'€|\s*EUR|kn', re.IGNORECASE))
                )
            
                price_text = ""
                if price_elem:
                    if isinstance(price_elem, str):
                        price_text = price_elem.strip()
                    else:
                        price_text = price_elem.get_text().strip()
            
                # Traži opis
                description_elem = (
                    container.find('p', class_=lambda x: x and any(k in str(x).lower() for k in ['desc', 'summary', 'excerpt'])) or
                    container.find('div', class_=lambda x: x and 'description' in str(x).lower())
                )
            
                description = ""
                if description_elem:
                    description = description_elem.get_text().strip()[:200]
            
                # Traži stanje (novo/rabljeno)
                condition_elem = (
                    container.find(string=re.compile(r'novo|rabljeno|korišteno|polovno|nekorišteno', re.IGNORECASE)) or
                    container.find('span', class_=lambda x: x and 'condition' in str(x).lower())
                )
            
                condition = "Nije navedeno"
                if condition_elem:
                    if isinstance(condition_elem, str):
                        condition_text = condition_elem.strip().lower()
                    else:
                        condition_text = condition_elem.get_text().strip().lower()
                
                    if 'novo' in condition_text or 'nekorišteno' in condition_text:
                        condition = "Novo"
                    elif 'rabljeno' in condition_text or 'korišteno' in condition_text or 'polovno' in condition_text:
                        condition = "Rabljeno"
            
                # Link na oglas
                link_elem = container.find('a', href=True)
                link = ""
                if link_elem:
                    link = link_elem.get('href', '')
                    if link and not link.startswith('http'):
                        link = f"https://www.njuskalo.hr{link}"
            
                if title and title not in seen_titles:
                    ad_data = {
                        'title': title,
                        'price': price_text or "Cijena nije navedena",
                        'description': description or "Nema opisa",
                        'condition': condition,
                        'link': link
                    }
                
                    ads.append(ad_data)
                    seen_titles.add(title)
                
                    if len(ads) >= 5:
                        break
        
            print(f"Pronađeno {len(ads)} oglasa\n")
            return ads[:5]
    
        except Exception as e:
            print(f"ERROR: Greška pri scrapingu: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_available_gemini_model():
        """Dohvati prvi dostupan Gemini model"""
        try:
            list_url = f"https://generativelanguage.googleapis.com/v1/models?key={GOOGLE_API_KEY}"
            list_response = requests.get(list_url)
        
            if list_response.status_code == 200:
                models_data = list_response.json()
                models = models_data.get('models', [])
            
                for model in models:
                    model_name = model.get('name', '')
                    supported_methods = model.get('supportedGenerationMethods', [])
                
                    if 'generateContent' in supported_methods and 'gemini' in model_name.lower():
                        return model_name.replace('models/', '')
        
            return "gemini-1.5-flash-latest"
        except Exception:
            return "gemini-1.5-flash-latest"

    def generate_ad_summary(ad):
        """Generiraj sažetak oglasa koristeći Gemini"""
    
        prompt = f"""Analiziraj sljedeći oglas za iPhone 17:

    Naslov: {ad['title']}
    Cijena: {ad['price']}
    Opis: {ad['description']}
    Stanje: {ad['condition']}

    Napiši detaljan sažetak oglasa u 3-4 rečenice na hrvatskom jeziku. Uključi:
    - Točan model i specifikacije (kapacitet, boja)
    - Cijenu i stanje uređaja
    - Posebne opcije ako postoje (rate, zamjena, garancija)
    - Lokaciju preuzimanja
    - Bilo što vrijedno napomenuti iz naslova ili opisa"""

        model_to_use = get_available_gemini_model()
    
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
    
        headers = {
            "Content-Type": "application/json"
        }
    
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models/{model_to_use}:generateContent?key={GOOGLE_API_KEY}"
            response = requests.post(url, json=payload, headers=headers)
        
            if response.status_code == 200:
                result = response.json()
                summary = result['candidates'][0]['content']['parts'][0]['text']
                return summary.strip()
            else:
                return "Nije moguće generirati sažetak."
    
        except Exception as e:
            return f"Greška pri generiranju sažetka: {str(e)}"

    def generate_pr_output(ads):
        """Generiraj PR output"""
    
        output = []
        output.append("=" * 80)
        output.append("PR OUTPUT - Njuškalo iPhone 17 Scraper")
        output.append("=" * 80)
        output.append("")
    
        output.append(f"Scraped URL: {SCRAPED_URL}")
        output.append("")
    
        output.append("Top 5 najjeftinijih iPhone 17 oglasa (raw text iz Steel-a):")
        output.append("-" * 80)
    
        for i, ad in enumerate(ads, 1):
            output.append(f"\n{i}. {ad['title']}")
            output.append(f"   Cijena: {ad['price']}")
            output.append(f"   Stanje: {ad['condition']}")
            output.append(f"   Opis: {ad['description']}")
            if ad.get('link'):
                output.append(f"   Link: {ad['link']}")
        
            # Generiraj sažetak
            print(f"Generiranje sažetka za oglas {i}...")
            summary = generate_ad_summary(ad)
            output.append(f"   LLM sažetak: {summary}")
    
        output.append("")
        output.append("Statistika:")
        output.append("-" * 80)
    
        novo_count = sum(1 for ad in ads if ad['condition'] == 'Novo')
        rabljeno_count = sum(1 for ad in ads if ad['condition'] == 'Rabljeno')
    
        output.append(f"  - Novo: {novo_count}")
        output.append(f"  - Rabljeno: {rabljeno_count}")
        output.append(f"  - Nije navedeno: {len(ads) - novo_count - rabljeno_count}")
    
        output.append("")
        output.append("=" * 80)
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("=" * 80)
    
        return "\n".join(output)

    def main():
        print("Njuškalo iPhone 17 Scraper")
        print("=" * 80)
        print()
    
        # Scrape oglase
        ads = scrape_njuskalo()
    
        if not ads:
            print("ERROR: Nisu pronađeni oglasi.")
            return
    
        # Generiraj PR output
        pr_output = generate_pr_output(ads)
        print("\n")
        print(pr_output)
    
        # Spremi rezultate
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
        # JSON output
        json_output = {
            "timestamp": timestamp,
            "scraped_url": SCRAPED_URL,
            "ads": ads,
            "total_found": len(ads)
        }
    
        json_filename = f"njuskalo_iphone17_{timestamp}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(json_output, f, ensure_ascii=False, indent=2)
    
        # PR output text file
        pr_filename = f"PR_OUTPUT_NJUSKALO_{timestamp}.txt"
        with open(pr_filename, "w", encoding="utf-8") as f:
            f.write(pr_output)
    
        print()
        print(f"Rezultati spremljeni:")
        print(f"   - JSON: {json_filename}")
        print(f"   - PR Output: {pr_filename}")

    if __name__ == "__main__":
        main()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
