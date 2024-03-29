"""
Get cookie via SAML.

> Roll out firefox only to get log-in cookies?

- This is fine :')
"""

import os
import time
from typing import List

import selenium
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By

from mousse.log import setup_logger

logger = setup_logger("mousse_saml")


def gib_cookies() -> List[dict]:
    """Log in and get cookie."""
    logger.debug("Getting cookies ...")

    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(options=opts)

    moses = "https://moseskonto.tu-berlin.de/moses/index.html"

    logger.debug("Loading moses ...")
    driver.get(moses)

    time.sleep(30)

    # login = driver.find_element(By.CSS_SELECTOR, "a[id*='shibboleth-login-form:j_idt'")
    try:
        login = driver.find_element(By.CSS_SELECTOR, "a[class*='nav-top-user-login'")
    except selenium.common.exceptions.NoSuchElementException as e:
        logger.warn("Error with login element")
        logger.warn(driver.current_url)
        logger.debug(driver.page_source)
        raise e
    login.click()

    time.sleep(30)

    username = driver.find_element(By.NAME, "j_username")
    password = driver.find_element(By.NAME, "j_password")

    if "SAML_USERNAME" not in os.environ or "SAML_PASSWORD" not in os.environ:
        raise ValueError("Please set env vars SAML_{USERNAME,PASSWORD}")

    username.send_keys(os.environ.get("SAML_USERNAME"))
    password.send_keys(os.environ.get("SAML_PASSWORD"))

    login = driver.find_element(By.ID, "login-button")

    logger.debug("Logging in ...")
    login.click()

    time.sleep(30)

    cookies = driver.get_cookies()

    time.sleep(10)

    logger.debug("Yummy.")

    driver.quit()

    return cookies
