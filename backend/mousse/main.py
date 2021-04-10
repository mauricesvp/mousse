"""
mousse.main

mauricesvp 2021
"""
import sys
import time

import bs4
from bs4 import BeautifulSoup as bs

import mousse.db as db
from mousse.log import setup_logger
from mousse.stupos import STUPOS
from mousse.utils import html_get, retry

sys.setrecursionlimit(20000)
logger = setup_logger("mousse_main")

moussedb: db.MousseDB
SEMESTER = "66"  # SOSE2021

SEMESTER_MAPPING = {
    "66": "SS2021",
    "67": "WS2021",
}


def get_rows(semester: str) -> list:
    url = degree_url(semester=semester, studiengang="", semesterStudiengang="", mkg="")
    r = html_get(url)
    soup = bs(r.text, "lxml")
    tbody = soup.find_all("tbody")[0]
    rows = tbody.find_all("tr")
    return rows


def get_modules(semester: str) -> None:
    rows = get_rows(semester)
    res = []
    for row in rows:
        module = process_row(row)
        if not module:
            continue
        module["id"] = module["id"].replace("#", "")
        module["version"] = module["version"].replace("v", "")
        res.append(module)

    global moussedb
    moussedb.add_modules(res)


def get_degree(id: str, stupo: str) -> None:
    semester = SEMESTER
    studiengang = id
    semesterStudiengang = semester

    url = degree_url(semester, studiengang, stupo, semesterStudiengang)
    logger.info(f"Getting degree {id}. URL: {url}")

    r = html_get(url=url)
    soup = bs(r.text, "lxml")
    tbody = soup.find_all("tbody")[0]
    rows = tbody.find_all("tr")
    name = soup.find(id="j_idt114:j_idt169_input")["value"]
    ba_or_ma = name.split("(")[-1][0]
    degree = {
        "name": name,
        "id": int(id),
        "semester": SEMESTER_MAPPING[semester],
        "ba_or_ma": ba_or_ma,
        "stupo": stupo,
    }
    modules = []
    for row in rows:
        row_info = get_row_info(row)
        if row_info:
            modules.append(row_info)
    degree["modules"] = modules

    global moussedb
    moussedb.add_degree(degree)


def get_row_info(row: bs4.element.Tag) -> tuple:
    try:
        tds = row.find_all("td")
        name = tds[3].contents[0].strip()
        number, version = tds[1].contents[0].split(" ")
        ects = tds[4].contents[0].strip()
        language = tds[6].contents[0].strip()
    except IndexError:
        print("Error with row:", row)
        raise
    if number and name and (ects is not None) and (version is not None) and language:
        return number, name, ects, version, language
    return ()


def process_row(row: bs4.element.Tag) -> dict:
    row_info = get_row_info(row)
    if not row_info:
        return {}
    number, name, ects, version, language = row_info
    if "Masterarbeit" not in name or "Bachelorarbeit" not in name:
        murl = module_url(number, version)
        parts = get_module(murl)
        if parts:
            return {
                "id": number,
                "name": name,
                "ects": ects,
                "version": version,
                "language": language,
                "module_parts": parts,
            }
    return {
        "id": number,
        "name": name,
        "ects": ects,
        "version": version,
        "language": language,
        "module_parts": [],
    }


def get_module(url: str) -> list:
    logger.info(f"Getting module at {url} .")
    parts = []

    r = html_get(url=url)
    # We don't want to get ip-banned I guess
    time.sleep(0.05)
    soup = bs(r.text, "lxml")

    th = soup.find("th", string="SWS")
    try:
        tbody = th.parent.parent
    except AttributeError as e:  # Probably some weird/outdated module
        logger.warning(f"Couldn't get module parts for {url} {th} {e}")
        return []
    rows = tbody.find_all("tr")
    len_rows = len(rows)
    for i in range(1, len_rows):
        try:
            row = rows[i]
            tds = row.find_all("td")
            name = tds[0].contents[0].strip()
            module_type = tds[1].contents[0].contents[0].strip()
            cycle = tds[3].contents[0].contents[0]
            parts.append(
                {
                    "name": name,
                    "module_type": module_type,
                    "cycle": cycle,
                }
            )
        except IndexError:  # e.g. Master thesis
            break

    return parts


def degree_url(
    semester: str, studiengang: str, mkg: str, semesterStudiengang: str
) -> str:
    return (
        f"https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/"
        f"suchen.html?semester={semester}&studiengang={studiengang}&mkg={mkg}"
        f"&semesterStudiengang={semesterStudiengang}"
    )


def module_url(number: str, version: str) -> str:
    number = number.replace("#", "")
    version = version.replace("v", "")
    return (
        f"https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/"
        f"beschreibung/anzeigen.html?number={number}&version={version}&sprache=2"
    )


@retry(5)
def init_db() -> None:
    global moussedb
    moussedb = db.MousseDB()
    while not moussedb:
        moussedb = db.MousseDB()


def export_modules() -> None:
    """
    1. Connect to mysql and get data (esp. JOINs)
    2. Build modules (This now happens in mousse.db.get_info)
    3. Post to solr (This also happens somewhere else now)
    """
    logger.info("Exporting data.")
    global moussedb
    data = moussedb.get_info()
    for x in data:
        # Integer version is needed for sorting
        x["ects_i"] = int(x["ects"])
        # String version is needed for filtering
        x["ects_str"] = int(x["ects"])
        # String version is needed for filtering
        # ('name' will be string too, but multiValued (solr magic))
        x["name_str"] = str(x["name"])
    with open("/mousse/data.json", "w+") as f:
        f.write(str(data))
    # At this point, you can run "./bin/post -c mousse_core /mousse/data.json"
    # (Within the solr container)


def main() -> None:
    init_db()
    while True:
        """Main loop:
        1. Scrape all modules and save to db ("modules" and "module_parts")
        2. Scrape all degrees and save to db ("degrees")
        3. Build junction table and save to db ("degree_modules")
        4. Build data.json and post to solr
          -> data.json gets copied over to solr via volumes
        5. Sleep and Repeat
        """
        get_modules(semester=SEMESTER)
        for s in STUPOS:
            get_degree(id=str(s), stupo=STUPOS[s])
        export_modules()
        time.sleep(3600 * 12)


if __name__ == "__main__":
    main()
