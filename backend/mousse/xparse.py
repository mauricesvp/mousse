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

logger = setup_logger("mousse_xparse")

XML_PARSER = lxml.etree.XMLParser(recover=True)


@retry(times=5)
def get_module_xml(url: str, r: Any = None) -> Any:
    """Return XML version of module as string."""
    if not r:
        r = html_get(url)
    text = re.search("(?<=<form)(.*)(?=form>)", r.text.replace("\n", "").strip())
    if text and hasattr(text, "group") and text.group:
        text = text.group(0)
    else:
        logger.warning("Error parsing XML", url)
        raise ValueError("Could not get XML", url, str(r))

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
        data=data,
        headers=headers,
        cookies=cookies,
    )
    xml_data = p2.content
    return xml_data


@retry(times=5)
def parse_xml(xml: str) -> dict:
    """Get module information."""
    try:
        root = lxml.etree.fromstring(xml, XML_PARSER)
    except Exception as e:
        logger.warn("Couldn't parse XML.", e)
        return {}
    # Namespaces
    ns = {"ns2": "http://data.europa.eu/europass/model/credentials#"}

    # Fak/Inst/FG
    fif = []
    try:
        fif = [
            x.text
            for x in root.findall(
                ".//ns2:agentReferences/ns2:organization/ns2:prefLabel", ns
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
                ".//ns2:assessmentSpecificationReferences"
                "/ns2:assessmentSpecification/ns2:type",
                ns,
            )[0]
            .get("uri")
            .split("/")[-1]
        )
    except IndexError:
        logger.warn("Could not get exam type.")
        raise
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
