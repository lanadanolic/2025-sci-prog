import marimo

__generated_with = "0.17.7"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    ################
    return


@app.cell
def _():
    import os
    import requests
    from dotenv import load_dotenv
    ##################
    return load_dotenv, os, requests


@app.cell
def _():
    from pathlib import Path
    #################
    return (Path,)


@app.cell
def _(Path, load_dotenv, os):
    script_folder = Path(__file__).parent
    dotenv_path = script_folder / ".env"  # dohvacanje sifra za apije
    load_dotenv(dotenv_path=dotenv_path)

    STEEL_API_KEY = os.getenv("steel_api")  # izvuci steel api kljuc u var
    # izvuci google ai api kljuc u var
    GEMINI_API_KEY = os.getenv("google_api")
    url = "https://www.scst.unist.hr/student/za-studente/ponuda-poslova"  # idemo trazit posao
    ##########
    return GEMINI_API_KEY, STEEL_API_KEY, url


@app.cell
def _(STEEL_API_KEY, requests, url):
    payload = {
        "url": url,
        "format": ["html"],
        "screenshot": False,
        "pdf": False,
        "delay": 1,
        "useProxy": False,
        "region": ""
    }

    headers = {
        "Content-Type": "application/json",
        "steel-api-key": STEEL_API_KEY
    }

    response = requests.post(
        "https://api.steel.dev/v1/scrape", headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        total_html = data["content"]["html"]
    else:
        print(response.text)

    print(total_html)
    #################
    return (total_html,)


@app.cell
def _(total_html):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(total_html, "html.parser")
    tables = soup.find_all('table')
    # print(tables) #izvlacenje podataka za pregled
    poslovi = soup.find_all('td')
    # print(naslovi) #izvlacenje poslova za strukturu (koliko je tesko pritisnuti enter i pomaknuti tag u novi red radi preglednosti?)
    for item in poslovi:
        print(item)
        print("############# kraj opisa ############")
    ###################
    return (soup,)


@app.cell
def _(soup):
    # izvlacenje podataka
    naslovi = soup.find_all(class_='posao-naslov')
    cijene = soup.find_all(class_='cijena')
    lok_pos = soup.find_all(class_='intro')
    #################
    return cijene, lok_pos, naslovi


@app.cell
def _(cijene, lok_pos, naslovi):
    # ciscenje podataka i formiranje stringova za analizu
    poslovi_bitno = []
    sep = " ; "
    for i in range(len(naslovi)):
        n = naslovi[i].text.strip()
        c = cijene[i].text.strip()
        l = lok_pos[i].text.strip()[:-2]
        bitno_kratko = n+sep+c+sep+l
        poslovi_bitno.append(bitno_kratko)

    return (poslovi_bitno,)


@app.cell
def _():
    from google import genai
    from google.genai import types
    ######################
    return (genai,)


@app.cell
def _(GEMINI_API_KEY, genai, poslovi_bitno):
    client = genai.Client(api_key=GEMINI_API_KEY)

    pitanje = "Analiziraj poslove sljedeće poslove, satnice i poslodavce :"
    for recenziraj in poslovi_bitno:
        pitanje += recenziraj
    pitanje += "\n Koji od ovih poslova bi bio najpogodniji za redovitog studenta? Uzmi u obzir da student nema novca i provodi 25 sati tjedno na fakultetu."
    response_google = client.models.generate_content(
        model="gemini-2.5-flash", contents=pitanje
    )
    print(response_google.text)
    return


if __name__ == "__main__":
    app.run()
