import re

import requests
from bs4 import BeautifulSoup as bs


def main():
    s = requests.Session()

    saved = {}

    SEM = "70"

    for i in range(4440, 6000):
        url = (
            "https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/suchen.html?text="
            f"&modulversionGueltigkeitSemester={SEM}"
            f"&studiengangSemester={SEM}"
            f"&studiengangBolognamodulliste={i}"
            "&studiengangsbereichWithChildren=true"
        )
        r = s.get(url, allow_redirects=False)

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
