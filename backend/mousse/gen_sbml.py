import re

import requests
import time
from bs4 import BeautifulSoup as bs

from mousse.utils import html_get


def main():
    s = requests.Session()

    saved = {}

    SEM = "71"

    for i in range(4440, 5500):
        time.sleep(1)
        url = (
            "https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/suchen.html?text="
            f"&modulversionGueltigkeitSemester={SEM}"
            f"&studiengangSemester={SEM}"
            f"&studiengangBolognamodulliste={i}"
            "&studiengangsbereichWithChildren=true"
        )
        # r = s.get(url, allow_redirects=False)
        r = html_get(url, bypass=True)

        if "Verwendung in Studiengang" not in r.text:
            continue

        soup = bs(r.text, "lxml")
        name = soup.find_all("td", colspan=True)[-1].text.strip()

        sem, sbml = re.search(
            r"'studiengangSemester', '(\d+)'\);;Moses\.Util\.UrlParam\.update\('studiengangBolognamodulliste', '(\d+)'",
            r.text,
        ).groups()

        if sem != SEM:
            continue

        saved[name] = sbml

    with open("sbml.py", "w") as f:
        f.write("SBML=")
        f.write(str(saved))


if __name__ == "__main__":
    main()
