from bs4 import BeautifulSoup
import requests

def Haus_page():
    url = "https://de.wiktionary.org/wiki/Haus"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    definitions = soup.find_all('ol')
    for definition in definitions:
        print(definition.get_text())