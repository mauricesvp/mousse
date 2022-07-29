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
    faces_suffix_lang = int(faces_prefix[-3:]) + 17
    faces_suffix_data = int(faces_prefix[-3:]) + 14

    VIEW_STATE = str(soup.find("input", {"name": "javax.faces.ViewState"})["value"])
    CLIENT_WINDOW = str(
        soup.find("input", {"name": "javax.faces.ClientWindow"})["value"]
    )

    del soup

    # cookies = r.cookies
    headers = {"Content-type": "application/x-www-form-urlencoded"}

    data = {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": f"{faces_source}",
        # "javax.faces.source": "j_idt106:j_idt117",
        # "javax.faces.source": "j_idt105:j_idt116",
        "javax.faces.partial.execute": "@all",
        "javax.faces.partial.render": f"{faces_prefix}",
        # "javax.faces.partial.render": "j_idt106",
        # "javax.faces.partial.render": "j_idt105",
        f"{faces_source}": f"{faces_source}",
        # "j_idt106:j_idt117": "j_idt106:j_idt117",
        # "j_idt105:j_idt116": "j_idt105:j_idt116",
        f"{faces_prefix}": f"{faces_prefix}",
        # "j_idt106": "j_idt106",
        # "j_idt105": "j_idt105",
        f"{faces_prefix}:j_idt{faces_suffix_lang}": "1",
        # "j_idt106:j_idt122": "1",  # 1: Deutsch, 2: English
        # "j_idt105:j_idt121": "1",
        "javax.faces.ViewState": VIEW_STATE,
        "javax.faces.ClientWindow": CLIENT_WINDOW,
    }
    html_post(
        url + f"&jfwid={CLIENT_WINDOW}",
        data=data,
        headers=headers,
        # cookies=cookies,
    )
    tmp = f"{faces_prefix}:j_idt{faces_suffix_data}"
    data = {
        f"{faces_prefix}": f"{faces_prefix}",
        # "j_idt106": "j_idt106",
        # "j_idt105": "j_idt105",
        f"{faces_prefix}:j_idt{faces_suffix_lang}": "1",
        # "j_idt106:j_idt122": "1",
        # "j_idt105:j_idt121": "1",
        "javax.faces.ViewState": VIEW_STATE,
        "javax.faces.ClientWindow": CLIENT_WINDOW,
        tmp: tmp,
        # "j_idt106:j_idt119": "j_idt106:j_idt119",
        # "j_idt105:j_idt118": "j_idt105:j_idt118",
    }
    p2 = html_post(
        url + f"&jfwid={CLIENT_WINDOW}",
        data=data,
        headers=headers,
        # cookies=cookies,
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
