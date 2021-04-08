# Iterate all degrees and save latest stupo
import requests
from bs4 import BeautifulSoup as bs


def gen_stupos() -> dict:
    stupos = {}
    for i in range(29, 400):
        url = (
            f"https://moseskonto.tu-berlin.de/moses/modultransfersystem/studiengaenge/"
            f"anzeigen.html?studiengang={i}"
        )
        r = requests.get(url)
        if "error" not in r.url:
            soup = bs(r.text, "lxml")
            select = soup.find(id="j_idt103:j_idt160")
            options = select.parent.find_all("option")
            newest = options[-1]["value"]
            stupos.update({i: newest})
    return stupos
