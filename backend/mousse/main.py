"""
Main script for mousse.

mauricesvp 2021
"""

# import csv
# import os
import re
import sys
import time
import traceback
from multiprocessing import Pool, cpu_count
from typing import Any, List, Tuple

import bs4
from bs4 import BeautifulSoup as bs

from mousse.db import MousseDB
from mousse.log import setup_logger
from mousse.mls_ws23 import MLS
from mousse.stupos_ws23 import STUPOS
from mousse.utils import array_split, html_get, login, retry
from mousse.xparse import alt_parse, get_module_xml, parse_xml

# Debugging
# from IPython import embed

sys.setrecursionlimit(20000)
logger = setup_logger("mousse_main")

moussedb: MousseDB

SEMESTER = "71"  # WISE2023

SEMESTER_MAPPING = {
    "71": "WS2023",
}

# Scrape modules in N batches
BATCHES = 40

# Delay between scraping in seconds
DELAY = 3600 * 20


@retry(times=5, debug=True)
def get_rows_csv(semester: str) -> list:
    """In case using csv export ever becomes necessary."""
    """
    modules = []
    # Nummer/Version,Modultitel,LP,Verantwortliche Person,Sprache,Zugehörigkeit
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../modules.csv")
    with open(path, "r") as f:
        reader = csv.reader(f, quoting=csv.QUOTE_ALL)
        next(reader, None)  # Skip header
        for row in reader:
            numver, name, ects, people, language, department = row

            if language == "":
                language = "DE/EN"

            number, version = numver.split(" ")
            number = number.replace("#", "")
            version = version.replace("v", "")

            dups = [x for x in modules if x[0] == number]
            if len(dups) > 1:
                raise ValueError("There shouldn't be more than one duplicate")
            if dups:
                if int(dups[0][3]) < int(version):
                    modules.remove(dups[0])
                else:
                    continue

            # number, name, ects, version, language
            modules.append((number, name, ects, version, language))

    return modules
    """
    raise NotImplementedError


@retry(times=5, debug=True)
def get_rows(semester: str) -> list:
    """Return all rows from MTS search result."""
    url = degree_url(
        semester=semester,
        studiengang="",
        modulversionGueltigkeitSemester=semester,
        mls="",
    )
    r = html_get(url, timeout=30)

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
    while True:
        rows = get_rows(semester)
        logger.info(f"Found {len(rows)} rows.")
        if len(rows) > 100:
            break
        time.sleep(60)
        login()  # get new cookies

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

        # Debugging
        if True:
            res = []
            for row in rows_str:
                test = process_row(row)
                # embed()
                # exit()
                res.append(test)
                time.sleep(1)

        else:
            with Pool(n) as pool:
                res = pool.map(process_row, rows_str)

        res = [x for x in res if x]
        keys = [
            "id",
            "name",
            "ects",
            "version",
            "language",
            "module_parts",
            "exam_type_str",
            "faculty",
            "institute",
            "group_str",
            "module_description",
            "test_description",
            "test_parts",
        ]
        for r in res:
            for key in keys:
                if key not in r:
                    logger.debug(r)
                    r[key] = ""

        global moussedb
        moussedb.add_modules(res)


@retry(times=10, delay=10, debug=True)
def get_degree(id: str, stupo: str, mls: str) -> None:
    """Get and update degree."""
    url = degree_url(SEMESTER, id, mls, SEMESTER)
    logger.info(f"Getting degree {id}. URL: {url}")

    try:
        r = html_get(url=url, timeout=10)

        soup = bs(r.text, "lxml")
        tbody = soup.find_all("tbody")[0]
        rows = tbody.find_all("tr")

        fullname = soup.find_all("td", colspan=True)[-1].text.strip()
        # name = fullname.split("(")[0].strip()
        # Use fullname bc some degrees are included multiple times with different StuPOs

        try:
            ba_or_ma = fullname.split("(")[1][0]
        except IndexError:
            logger.debug(f"IndexError fullname {fullname}")
            raise

        degree = {
            "name": fullname,
            "id": int(id),
            "semester": SEMESTER_MAPPING[SEMESTER],
            "ba_or_ma": ba_or_ma,
            "stupo": stupo,
        }
        modules = []
    except Exception:
        logger.debug(traceback.format_exc())
        # logger.debug(e)
        raise
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
        language_block = tds[6]
        if language_block.contents:
            language = tds[6].contents[0].strip()
        else:
            language = "DE/EN"

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
    r = None
    if "Masterarbeit" not in name and "Bachelorarbeit" not in name:
        murl = module_url(number, version)
        r, parts = get_module(murl)
        if not r:
            logger.info(f"Problem with module {number}")
        else:
            logger.debug(f"{r.status_code} {number}")

        if len(parts) == 0:
            logger.debug(f"Empty parts! {number}")

        try:
            # Reuse request
            xinfo = alt_parse(murl, r=r)
            # data = get_module_xml(murl, r=r)
            # xinfo = parse_xml(data)
            assert xinfo is not None and "exam_type_str" in xinfo
        except AssertionError:
            # Try again
            xinfo = alt_parse(murl)
            # data = get_module_xml(murl)
            # xinfo = parse_xml(data)

        if xinfo is None:
            logger.debug(f"No exam/chair info (module {number}, data {len(data)})")
            logger.debug(str(xinfo))
            xinfo = {}

        exam_type_str = xinfo.get("exam_type_str", "")
        faculty = xinfo.get("faculty", "")
        institute = xinfo.get("institute", "")
        group_str = xinfo.get("group", "")

    # Test elements
    if False and r and exam_type_str == "continuous":
        soup = bs(r.text, "lxml")

        try:
            faces_source = soup.find(string=re.compile("Generate XML")).parent["id"]
        except AttributeError:
            faces_source = soup.find(string=re.compile("XML generieren")).parent["id"]
        faces_prefix = faces_source.split(":")[0]

        test_description = soup.find(
            "span", id=f"{faces_prefix}:pruefungsbeschreibungsbox"
        )
        try:
            test_description = test_description.find_all("span")[1].text
        except IndexError:
            test_description = ""

        try:
            test_elements = (
                soup.find("span", id=f"{faces_prefix}:studienleistungtabelle")
                .find("table")
                .find_all("tr")[1:]
            )
        except (IndexError, AttributeError):
            test_elements = []

        def test_part(tr: bs4.element.Tag) -> List[str]:
            tmp = tr.find_all("td")
            parts = [x.text.strip() for x in tmp]
            return parts

        test_parts = [test_part(tr) for tr in test_elements]

    else:
        test_description = ""
        test_parts = []

    if exam_type_str == "unknown":
        logger.error(f"unknown exam type {number}")

    # Learning outcomes and content
    description = ""
    if r is not None:

        def get_description(soup: bs4.element.Tag) -> str:
            h3s = soup.find_all("h3")
            try:
                if h3s[2].text not in ["Lernergebnisse", "Learning Outcomes"]:
                    return ""
                # No comment ...
                first_div = h3s[2].parent.parent.parent.parent.parent
                second_div = first_div.find_next_sibling("div")
            except (IndexError, AttributeError):
                return ""

            def get_text(element: bs4.element.Tag) -> str:
                area = element.find(class_="preformatedTextarea")
                if area is not None:
                    return area.text.strip()
                return ""

            first_text = get_text(first_div)
            second_text = get_text(second_div)

            return "\n".join(filter(None, [first_text, second_text]))

        soup = bs(r.text, "lxml")
        description = get_description(soup)

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
        "module_description": description,
        "test_description": test_description,
        "test_parts": test_parts,
    }


@retry(times=10, delay=10, debug=True)
def get_module(url: str) -> Tuple[Any, list]:
    """Get module parts."""
    parts = []

    r = html_get(url=url, bypass=True)
    soup = bs(r.text, "lxml")

    th = soup.find("th", string="SWS")
    try:
        table = th.parent.parent.parent
    except:  # noqa: E722
        return None, []

    rows = table.find_all("tr")
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
    semester: str, studiengang: str, mls: str, modulversionGueltigkeitSemester: str
) -> str:
    """Construct MTS degree url."""
    if mls:
        return (
            f"https://moseskonto.tu-berlin.de"
            f"/moses/modultransfersystem/bolognamodule/suchen.html?"
            f"studiengangSemester={semester}"
            f"&studiengangBolognamodulliste={mls}"
            f"&modulversionGueltigkeitSemester={modulversionGueltigkeitSemester}"
            f"&studiengangsbereichWithChildren=true"
        )
    return (
        "https://moseskonto.tu-berlin.de"
        "/moses/modultransfersystem/bolognamodule/suchen.html?"
        f"semester={semester}&"
        f"studiengang={studiengang}&"
        f"studiengangBolognamodulliste={mls}"
        f"&modulversionGueltigkeitSemester={modulversionGueltigkeitSemester}"
    )


def module_url(number: str, version: str) -> str:
    """Construct MTS module url."""
    number = number.replace("#", "")
    version = version.replace("v", "")
    return (
        f"https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/"
        f"beschreibung/anzeigen.html?number={number}&version={version}"
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


@retry(5, debug=True)
def init_db() -> None:
    """Init (python) db instance (actual db is init. already)."""
    global moussedb
    moussedb = MousseDB()
    while not moussedb:
        moussedb = MousseDB()


def main() -> None:
    """Init and run."""
    logger.info("Starting mousse main.")

    init_db()
    logger.debug("DB connected.")

    while True:
        """Main loop:
        1. Scrape all modules and save to db ("modules" and "module_parts")
        2. Scrape all degrees and save to db ("degrees")
        3. Build junction table and save to db ("degree_modules")
        4. Build data.json and post to solr
          -> data.json gets copied over to solr via volumes
        5. Sleep and Repeat
        """
        login()  # get new cookies
        get_modules(semester=SEMESTER)
        login()  # Getting modules might take long (hours), re-login
        SK, SV = list(STUPOS.keys()), list(STUPOS.values())
        MK, MV = list(MLS.keys()), list(MLS.values())
        for i in range(len(STUPOS)):  # TODO: Multithreaded
            assert SV[i] == MV[i]
            get_degree(id=SV[i], stupo=SK[i], mls=MK[i])

        export_modules()

        logger.info(f"Going to sleep .. ({DELAY} seconds)")
        time.sleep(DELAY)


if __name__ == "__main__":
    main()
