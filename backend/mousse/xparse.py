"""
mousse.xparse

mauricesvp 2021
"""
import re
from multiprocessing import Pool, cpu_count

import bs4
import lxml
import requests
from bs4 import BeautifulSoup as BS

from mousse.log import setup_logger
from mousse.main import degree_url, get_row_info, module_url
from mousse.utils import html_get, html_post

logger = setup_logger("mousse_xparse")

XML_PARSER = lxml.etree.XMLParser(recover=True)


def get_module_xml(url: str) -> str:
    r = None
    while not r:
        r = html_get(url)
        if r:
            break
    # We need to filter the html before we pass it to bs4
    # Otherwise we would get max. recursion errors.
    # This is due to multiprocessing pickling every variable.
    text = re.search("(?<=<form)(.*)(?=form>)", r.text.replace("\n", "").strip())
    if text and hasattr(text, "group") and text.group:
        text = text.group(0)
    else:
        logger.warning("Error parsing XML", url)
        return ""

    soup = BS(text, "lxml")
    VIEW_STATE = str(soup.find("input", {"name": "javax.faces.ViewState"})["value"])
    CLIENT_WINDOW = str(
        soup.find("input", {"name": "javax.faces.ClientWindow"})["value"]
    )
    del soup
    cookies = r.cookies
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    data = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": "j_idt106:j_idt117",
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": "j_idt106",
        "j_idt106:j_idt117": "j_idt106:j_idt117",
        "j_idt106": "j_idt106",
        "j_idt106:j_idt122": "1",
        "javax.faces.ViewState": VIEW_STATE,
        "javax.faces.ClientWindow": CLIENT_WINDOW,
    }
    html_post(
        url + f"&jfwid={CLIENT_WINDOW}",
        timeout=20,
        data=data,
        headers=headers,
        cookies=cookies,
    )
    data = {
        "j_idt106": "j_idt106",
        "j_idt106:j_idt122": "1",
        "javax.faces.ViewState": VIEW_STATE,
        "javax.faces.ClientWindow": CLIENT_WINDOW,
        "j_idt106:j_idt119": "j_idt106:j_idt119",
    }
    p2 = html_post(
        url + f"&jfwid={CLIENT_WINDOW}",
        timeout=20,
        data=data,
        headers=headers,
        cookies=cookies,
    )
    xml_data = p2.content
    return xml_data


def parse_xml(xml: str) -> dict:
    """Get module information."""

    try:
        root = lxml.etree.fromstring(xml, XML_PARSER)
    except Exception as e:
        print("Error with xml", xml, e)
        return {}
    # Namespaces
    ns = {"ns2": "http://data.europa.eu/europass/model/credentials#"}

    # Fak/Inst/FG
    fif = [
        x.text
        for x in root.findall(
            ".//ns2:agentReferences/ns2:organization/ns2:prefLabel", ns
        )
    ]
    faculty, institute, group = None, None, None
    if len(fif) > 1:
        faculty = fif[1]
    if len(fif) > 2:
        institute = fif[2]
    if len(fif) > 3:
        group = fif[3]

    # Person in charge
    # TODO: Where do we get this info from?

    # Method of examination
    try:
        exam_type = (
            root.findall(
                ".//ns2:assessmentSpecificationReferences"
                "/ns2:assessmentSpecification/ns2:type",
                ns,
            )[0]
            .get("uri")
            .split("/")[-1]
        )
    except IndexError:
        print("Could not get exam type", root)
        exam_type = ""
    if "oral" in exam_type:
        exam_type = "oral"
    elif "written" in exam_type:
        exam_type = "written"
    elif "continuous" in exam_type:
        exam_type = "continuous"
    elif "marked" in exam_type:
        exam_type = "none"
    else:
        exam_type = "unknown"

    information = dict()
    if faculty:
        information.update({"faculty": faculty})
    if institute:
        information.update({"institute": institute})
    if group:
        information.update({"group": group})
    # Add _str for solr
    information.update({"exam_type_str": exam_type})
    return information


def process_row(row: bs4.element.Tag) -> dict:
    row = BS(row[0], "lxml")
    row_info = get_row_info(row)
    if not row_info:
        return {}
    number, name, ects, version, language = row_info
    murl = module_url(number, version)
    data = get_module_xml(murl)
    if not data:
        return {}
    return {
        "id": number.replace("#", ""),
        "version": version.replace("v", ""),
        **parse_xml(data),
    }


def get_stuff() -> None:
    semester = "66"
    url = degree_url(semester=semester, studiengang="", semesterStudiengang="", mkg="")
    r = requests.get(url)
    soup = BS(r.text, "lxml")
    tbody = soup.find_all("tbody")[0]
    rows = tbody.find_all("tr")
    rows_str = [[str(x)] for x in rows]
    res = []
    n = (cpu_count() * 2) - 1
    logger.info(f"Getting {len(rows_str)} rows.")
    with Pool(n) as pool:
        res = pool.map(process_row, rows_str)

        # Filter modules with multiple versions (only keep newest one)
        ids = [x["id"] for x in res]
        duplicates = set(i for i in ids if ids.count(i) > 1)
        for x in duplicates:
            max_version = 0
            tmp = {}
            # We delete each version, save the currently highest,
            # and insert that one back in the end
            for y in [z for z in res if z["id"] == x]:
                curr_version = int(y["version"].replace("v", ""))
                if curr_version > max_version:
                    max_version = curr_version
                    tmp = y
                    res.remove(y)
            res.append(tmp)

        with open("ext_data.json", "w+") as f:
            f.write(str(res))


get_stuff()
