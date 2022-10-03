"""
Latest stupo and module lists.

mauricesvp 2021
"""
from typing import Tuple

from bs4 import BeautifulSoup as bs

from mousse.log import setup_logger
from mousse.utils import html_get

logger = setup_logger("mousse_mkg")


def calc_sem(inp: str) -> str:
    """
    Convert semester.

    ss21 -> 66
    ws20 -> 65
    ..
    .
    ss88 -> 0
    """
    try:
        _, cycle, year_str = inp.split()
    except ValueError:
        cycle, year_str = inp.split()
    year_str = year_str.split("/")[0]
    year = int(year_str)
    ws = 0 if ("SoSe" in cycle or "SS" in cycle) else 1
    calc = ((year - 1988) * 2) + ws
    return str(calc)


def gen_degrees() -> Tuple[dict, dict, dict]:
    """Return newest stupo and module list for each degree."""
    stupos = {}
    mls = {}
    mls_id = {}
    for i in range(29, 400):
        logger.debug(f"Trying degree {i}.")
        url = (
            f"https://moseskonto.tu-berlin.de/moses/modultransfersystem/studiengaenge/"
            f"anzeigen.html?studiengang={i}"
        )
        r = html_get(url, bypass=True, timeout=5)
        if not r or "error" in r.url or "shibboleth" in r.url:
            continue

        soup = bs(r.text, "lxml")
        select_stupo = soup.find(id="j_idt108:j_idt165")
        options_stupo = select_stupo.parent.find_all("option")
        if len(options_stupo) <= 1:
            continue

        newest_stupo = options_stupo[-1]["value"]
        stupos.update({i: newest_stupo})

        # module list (e.g. SS2021)
        # select_ml = soup.find(id="j_idt103:j_idt166")

        try:
            select_ml = soup.find(id="j_idt108:j_idt171")
            options_ml = select_ml.parent.find_all("option")
        except AttributeError:
            select_ml = soup.find(id="j_idt108:j_idt177")
            options_ml = select_ml.parent.find_all("option")

        newest_ml = None
        nml = None
        if len(options_ml) > 1:
            newest_ml = options_ml[1].text
            nml = calc_sem(newest_ml)
            mls.update({i: nml})

            mls_id.update({i: options_ml[1]["value"]})

        logger.debug(f"Found newest stupo {newest_stupo} and module list {nml}.")

    return stupos, mls, mls_id


if __name__ == "__main__":
    import json

    stupos, mls, mls_id = gen_degrees()

    SEMESTER = "69"
    NAME = "ws22"

    bk = stupos.copy()
    for key in stupos:
        if key not in mls or mls[key] != SEMESTER:
            del bk[key]
    with open(f"stupos_{NAME}.py", "w") as f:
        f.write("STUPOS=")
        json.dump(bk, f)

    bk2 = bk.copy()
    for key in bk:
        if int(mls_id[key]) < 100:
            del bk2[key]
        else:
            bk2[key] = mls_id[key]
    with open(f"mls_{NAME}.py", "w") as f:
        f.write("MLS=")
        json.dump(bk2, f)
