"""
XML parsing.

mauricesvp 2021
"""

import re
from typing import Any

import lxml
from bs4 import BeautifulSoup as BS

from mousse.log import setup_logger
from mousse.utils import html_get, html_post, retry

# from IPython import embed

logger = setup_logger("mousse_xparse")

XML_PARSER = lxml.etree.XMLParser(recover=True)


@retry(times=5, debug=True)
def get_degree_xml(url: str, timeout: int = 10) -> Any:
    """Get degree via POST."""
    r = html_get(url=url, timeout=timeout)

    soup = BS(r.text, "lxml")

    # j_idtxxx:j_idtxxx
    faces_source = soup.find(text=re.compile("Module suchen")).parent["id"]

    faces_prefix = faces_source.split(":")[0]
    # TODO: plz no hardcode
    faces_suffix_lang = int(faces_prefix.replace("j_idt", "")) + 3

    VIEW_STATE = str(soup.find("input", {"name": "javax.faces.ViewState"})["value"])
    CLIENT_WINDOW = str(
        soup.find("input", {"name": "javax.faces.ClientWindow"})["value"]
    )

    del soup

    headers = {"Content-type": "application/x-www-form-urlencoded", "Referer": url}

    data = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": f"{faces_source}",
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": f"{faces_prefix}",
        f"{faces_source}": f"{faces_source}",
        f"{faces_prefix}": f"{faces_prefix}",
        f"{faces_prefix}:j_idt{faces_suffix_lang}": "1",
        "javax.faces.ViewState": VIEW_STATE,
        "javax.faces.ClientWindow": CLIENT_WINDOW,
    }
    p1 = html_post(
        url + f"&jfwid={CLIENT_WINDOW}",
        data=data,
        headers=headers,
    )

    return p1


@retry(times=5, debug=True)
def get_module_xml(url: str, r: Any = None) -> Any:
    """Return XML version of module as string."""
    if not r:
        r = html_get(url)
    text_raw = re.search("(?<=<form)(.*)(?=form>)", r.text.replace("\n", "").strip())
    if text_raw and hasattr(text_raw, "group") and text_raw.group:
        text = text_raw.group(0)
    else:
        logger.warning("Error parsing XML")
        logger.warning(url)
        raise ValueError("Could not get XML", url, str(r))

    soup = BS(text, "lxml")

    # j_idtxxx:j_idtxxx
    try:
        faces_source = soup.find(text=re.compile("Generate XML")).parent["id"]
    except AttributeError:
        faces_source = soup.find(text=re.compile("XML generieren")).parent["id"]

    faces_prefix = faces_source.split(":")[0]
    # TODO: plz no hardcode
    faces_suffix_lang = int(faces_prefix.replace("j_idt", "")) + 3
    faces_suffix_data = int(faces_prefix.replace("j_idt", "")) + 19

    VIEW_STATE = str(soup.find("input", {"name": "javax.faces.ViewState"})["value"])
    CLIENT_WINDOW = str(
        soup.find("input", {"name": "javax.faces.ClientWindow"})["value"]
    )

    del soup

    headers = {"Content-type": "application/x-www-form-urlencoded"}

    data = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": f"{faces_source}",
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": f"{faces_prefix}",
        f"{faces_source}": f"{faces_source}",
        f"{faces_prefix}": f"{faces_prefix}",
        f"{faces_prefix}:j_idt{faces_suffix_lang}": "1",
        "javax.faces.ViewState": VIEW_STATE,
        "javax.faces.ClientWindow": CLIENT_WINDOW,
    }
    html_post(
        url + f"&jfwid={CLIENT_WINDOW}",
        data=data,
        headers=headers,
    )
    tmp = f"{faces_prefix}:j_idt{faces_suffix_data}"
    data = {
        f"{faces_prefix}": f"{faces_prefix}",
        f"{faces_prefix}:j_idt{faces_suffix_lang}": "1",
        "javax.faces.ViewState": VIEW_STATE,
        "javax.faces.ClientWindow": CLIENT_WINDOW,
        tmp: tmp,
    }
    p2 = html_post(
        url + f"&jfwid={CLIENT_WINDOW}",
        data=data,
        headers=headers,
    )
    xml_data = p2.content
    return xml_data


@retry(times=5)
def parse_xml(xml: str) -> dict:
    """Get module information."""
    try:
        root = lxml.etree.fromstring(xml, XML_PARSER)
    except Exception as e:
        logger.warn("Couldn't parse XML.")
        logger.warn(e)
        return {}

    # Namespaces
    # ns = {"ns2": "http://data.europa.eu/europass/model/credentials#"}
    ns = {"ns5": "http://data.europa.eu/snb"}

    # Fak/Inst/FG
    fif = []
    try:
        fif = [
            x.text
            for x in root.findall(
                # ".//ns2:agentReferences/ns2:organization/ns2:prefLabel", ns
                ".//ns5:agentReferences/ns5:organization/ns5:prefLabel/ns5:text",
                ns,
            )
        ]
    except Exception as e:
        logger.warn("Couldn't determine departments.", e)
        raise

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
                # ".//ns2:assessmentSpecificationReferences"
                ".//ns5:assessmentSpecificationReferences"
                # "/ns2:assessmentSpecification/ns2:type",
                "/ns5:assessmentSpecification/ns5:type",
                ns,
            )[0]
            .get("uri")
            .split("/")[-1]
        )
    except IndexError:
        # logger.warn("Could not get exam type.")
        raise
    # if "oral" in exam_type:
    if "d30284d7df" in exam_type:
        exam_type = "oral"
    # elif "written" in exam_type:
    elif "6e6cb2cc78" in exam_type:
        exam_type = "written"
    # elif "continuous" in exam_type:
    elif "4f03b91c0e" in exam_type:
        exam_type = "continuous"
    # elif "marked" in exam_type:
    elif "2939dae15f" in exam_type:
        exam_type = "paper"  # Referat/Hausarbeit/Abschlussarbeit
    elif "3484bd7e51" in exam_type:
        exam_type = "internship"  # (Internes) Praktikum
    elif "7331eb4762" in exam_type:
        exam_type = "none"
    else:
        exam_type = "unknown"
    # TODO: Add Hausarbeit etc.

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


@retry(times=10, debug=True)
def alt_parse(url: str, r: Any = None) -> dict:
    """Alternative version; parse module description html"""
    if not r:
        r = html_get(url)
    text = r.text

    soup = BS(text, "lxml")

    boxes = soup.find_all(class_="cardWithSameHeight")

    try:
        exam_type = (
            boxes[0]
            .find_all(class_="col-xs-12 col-md-8")[-1]
            .find("span")
            .get_text()
            .strip()
        )
        etl = exam_type.lower()
        if "portfolio" in etl:
            exam_type = "continuous"
        elif "oral" in etl or "mündlich" in etl:
            exam_type = "oral"
        elif "schriftlich" in etl or "written" in etl:
            exam_type = "written"
        elif "referat" in etl or "hausarbeit" in etl or "abschlussarbeit" in etl:
            exam_type = "paper"  # Referat/Hausarbeit/Abschlussarbeit
        elif "praktikum" in etl:
            exam_type = "internship"  # (Internes) Praktikum
        elif "keine" in etl:
            exam_type = "none"
        else:
            exam_type = "unknown"
    except IndexError as e:
        logger.warn(f"Issue with {url}")
        logger.warn(f"{type(boxes)}")
        logger.warn(e)
        logger.debug(text)
        raise

    lines = boxes[1].find_all(class_="col-xs-12")
    faculty = lines[1].get_text().split(":")[-1].strip()
    institute = lines[2].get_text().split(":")[-1].strip()
    group = lines[3].get_text().split(":")[-1].strip()

    # print(exam_type, faculty, institute, group)
    # embed()
    # exit()

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
