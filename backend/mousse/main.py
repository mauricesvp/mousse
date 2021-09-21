"""
Main script for mousse.

mauricesvp 2021
"""
import sys
import time
from multiprocessing import Pool, cpu_count
from typing import Any, Tuple

import bs4
from bs4 import BeautifulSoup as bs

import mousse.db as db
from mousse.log import setup_logger

# from mousse.stupos import STUPOS
from mousse.stupos_ws21 import STUPOS
from mousse.utils import array_split, html_get, retry
from mousse.xparse import get_module_xml, parse_xml

sys.setrecursionlimit(20000)
logger = setup_logger("mousse_main")

moussedb: db.MousseDB

SEMESTER = "67"  # WISE2021
# SEMESTER = "66"  # SOSE2021
SEMESTER_MAPPING = {
    "66": "SS2021",
    "67": "WS2021",
}

# Scrape modules in N batches
BATCHES = 20

# Delay between scraping in seconds
DELAY = 3600 * 6


@retry(times=5)
def get_rows(semester: str) -> list:
    """Return all rows from MTS search result."""
    url = degree_url(semester=semester, studiengang="", semesterStudiengang="", mkg="")
    r = html_get(url)
    soup = bs(r.text, "lxml")
    tbody = soup.find_all("tbody")[0]
    rows = tbody.find_all("tr")
    assert isinstance(rows, list)
    return rows


def pre_process_rows(rows: list) -> list:
    """Filter old module versions."""
    row_infos: list = []
    for row in rows:
        row_info = get_row_info(row)
        if row_info:
            dup = [x for x in row_infos if x[0] == row_info[0]]
            if dup:
                row_infos.remove(dup[0])
            row_infos.append(row_info)
    return row_infos


def get_modules(semester: str) -> None:
    """Get and update all modules."""
    rows = get_rows(semester)
    logger.info(f"Found {len(rows)} rows.")
    # Filter old module versions
    rows_info = pre_process_rows(rows)
    logger.info(f"Got {len(rows_info)} rows left after filtering.")
    # Divide rows in chunks
    chunks = array_split(rows_info, BATCHES)
    n = cpu_count() - 1
    for i, chunk in enumerate(chunks):
        logger.info(f"Processing batch {i+1}/{len(chunks)} ({len(chunk)} rows).")
        res = []
        rows_str = [[x] for x in list(chunk)]

        with Pool(n) as pool:
            res = pool.map(process_row, rows_str)

        res = [x for x in res if x]
        global moussedb
        moussedb.add_modules(res)


@retry(times=5, delay=2)
def get_degree(id: str, stupo: str) -> None:
    """Get and update degree."""
    semester = SEMESTER
    studiengang = id
    semesterStudiengang = semester

    url = degree_url(semester, studiengang, stupo, semesterStudiengang)
    logger.info(f"Getting degree {id}. URL: {url}")

    r = html_get(url=url)
    soup = bs(r.text, "lxml")
    tbody = soup.find_all("tbody")[0]
    rows = tbody.find_all("tr")
    # name = soup.find(id="j_idt114:j_idt169_input")["value"]
    name = soup.find(id="j_idt113:j_idt168_input")["value"]
    ba_or_ma = name.split("(")[-1][0]
    degree = {
        "name": name,
        "id": int(id),
        "semester": SEMESTER_MAPPING[semester],
        "ba_or_ma": ba_or_ma,
        "stupo": stupo,
    }
    modules = []
    logger.debug(f"Found {len(rows)} modules.")
    for row in rows:
        row_info = get_row_info(row)
        if row_info:
            modules.append(row_info)
    degree["modules"] = modules

    global moussedb
    moussedb.add_degree(degree)


def get_row_info(row: bs4.element.Tag) -> tuple:
    """Get info from module row."""
    try:
        tds = row.find_all("td")
        name = tds[3].contents[0].strip()
        number, version = tds[1].contents[0].split(" ")
        number = number.replace("#", "")
        version = version.replace("v", "")
        ects = tds[4].contents[0].strip()
        language = tds[6].contents[0].strip()
    except IndexError:
        logger.error("Error with row:", row)
        raise
    if number and name and (ects is not None) and (version is not None) and language:
        return number, name, ects, version, language
    return ()


def process_row(row_info: list) -> dict:
    """Scrape module from row info."""
    row_info = row_info[0]
    try:
        number, name, ects, version, language = row_info
    except ValueError:
        print(row_info)
        raise
    parts = []
    exam_type_str = ""
    faculty = ""
    institute = ""
    group_str = ""
    if "Masterarbeit" not in name or "Bachelorarbeit" not in name:
        murl = module_url(number, version)
        r, parts = get_module(murl)

        try:
            # Reuse request
            data = get_module_xml(murl, r=r)
            xinfo = parse_xml(data)
            assert xinfo is not None and "exam_type_str" in xinfo
        except AssertionError:
            # Try again
            data = get_module_xml(murl)
            xinfo = parse_xml(data)

        if xinfo is None:
            xinfo = {}

        exam_type_str = xinfo.get("exam_type_str", "")
        faculty = xinfo.get("faculty", "")
        institute = xinfo.get("institute", "")
        group_str = xinfo.get("group", "")
    if exam_type_str == "unknown":
        logger.error(f"unknown exam type {number}")
    return {
        "id": number,
        "name": name,
        "ects": ects,
        "version": version,
        "language": language,
        "module_parts": parts,
        "exam_type_str": exam_type_str,
        "faculty": faculty,
        "institute": institute,
        "group_str": group_str,
    }


@retry(times=5)
def get_module(url: str) -> Tuple[Any, list]:
    """Get module parts."""
    parts = []

    r = html_get(url=url)
    soup = bs(r.text, "lxml")

    th = soup.find("th", string="SWS")
    try:
        tbody = th.parent.parent
    except:  # noqa: E722
        return None, []
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

    return r, parts


def degree_url(
    semester: str, studiengang: str, mkg: str, semesterStudiengang: str
) -> str:
    """Construct MTS degree url."""
    return (
        f"https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/"
        f"suchen.html?semester={semester}&studiengang={studiengang}&mkg={mkg}"
        f"&semesterStudiengang={semesterStudiengang}"
    )


def module_url(number: str, version: str) -> str:
    """Construct MTS module url."""
    number = number.replace("#", "")
    version = version.replace("v", "")
    return (
        f"https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/"
        f"beschreibung/anzeigen.html?number={number}&version={version}&sprache=2"
    )


def export_modules() -> None:
    """
    Get data from db and export as json.

    1. Connect to mysql and get data (esp. JOINs).
    2. Build modules (This now happens in mousse.db.get_info).
    3. Post to solr (This also happens somewhere else now).
    """
    logger.info("Exporting data.")
    global moussedb
    data = moussedb.get_info()
    for x in data:
        # Integer version is needed for sorting
        # String version is needed for filtering

        x["ects_i"] = int(x["ects"])
        x["ects_str"] = str(x["ects"])
        x["name_str"] = str(x["name"])
        x["group"] = str(x["group_str"])
        x["institute_str"] = str(x["institute"])
    with open("data.json", "w+") as f:
        f.write(str(data))
    # At this point, you can run "./bin/post -c mousse_core /mousse/data.json"
    # (Within the solr container)


@retry(5)
def init_db() -> None:
    """Init (python) db instance (actual db is init. already)."""
    global moussedb
    moussedb = db.MousseDB()
    while not moussedb:
        moussedb = db.MousseDB()


def main() -> None:
    """Init and run."""
    logger.info("Starting mousse main.")
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
        logger.info(f"Going to sleep .. ({DELAY} seconds)")
        time.sleep(DELAY)


if __name__ == "__main__":
    main()
