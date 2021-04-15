"""
mousse.blocks
----
Consider this beta-ish

mauricesvp 2021
"""
import requests
from bs4 import BeautifulSoup as bs

from mousse.log import setup_logger

logger = setup_logger("mousse_blocks")


def get_block_courses() -> list:
    """Scrape ISIS for block courses."""
    logger.info("Getting block courses.")
    course_names = []

    # 'blockveranstaltung'
    r = requests.get(
        "https://isis.tu-berlin.de/course/search.php?"
        "search=blockveranstaltung&perpage=all"
    )
    soup = bs(r.text, "lxml")
    stuff = soup.find_all(class_="coursename")
    for x in stuff:
        course_names.append(x.a.text)

    # 'blockseminar'
    r = requests.get(
        "https://isis.tu-berlin.de/course/search.php?search=blockseminar&perpage=all"
    )
    soup = bs(r.text, "lxml")
    stuff = soup.find_all(class_="coursename")
    for x in stuff:
        name = x.a.text
        if "blockseminar" in name.lower():
            course_names.append(name)

    # TODO: Match against module list

    return course_names
