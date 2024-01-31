"""
Latest stupo and module lists.

mauricesvp 2021
"""

from typing import Tuple

import requests
import time
from bs4 import BeautifulSoup as bs

from mousse.log import setup_logger
from mousse.sbml import SBML
from mousse.utils import html_get

logger = setup_logger("mousse_mkg")


def gen_degrees() -> Tuple[dict, dict, dict]:
    """Return newest stupo and module list for each degree."""
    s = requests.Session()

    stupos = {}
    mls_id = {}
    for i in range(20, 260):
        logger.debug(f"Trying degree {i}.")
        time.sleep(5)
        url = (
            f"https://moseskonto.tu-berlin.de/moses/modultransfersystem/studiengaenge/"
            f"anzeigen.html?studiengang={i}"
        )
        # r = s.get(url)
        r = html_get(url, bypass=True)
        if not r or "error" in r.url or "shibboleth" in r.url:
            continue

        soup = bs(r.text, "lxml")
        selects = soup.find_all("select")
        options_stupo = selects[0].find_all("option")
        if len(options_stupo) <= 1:
            continue

        for j, stupo in enumerate(options_stupo[1:]):
            i = str(i)
            stupo_name = stupo.text.strip()
            if stupo_name in SBML:
                stupo_id = options_stupo[j + 1]["value"]
                stupos.update({stupo_id: i})
                mls_id.update({SBML[stupo_name]: i})

    return stupos, mls_id


if __name__ == "__main__":
    import json

    stupos, mls_id = gen_degrees()

    NAME = "ws23"

    with open(f"stupos_{NAME}.py", "w") as f:
        f.write("STUPOS=")
        json.dump(stupos, f)

    with open(f"mls_{NAME}.py", "w") as f:
        f.write("MLS=")
        json.dump(mls_id, f)
