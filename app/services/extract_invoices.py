import time
from playwright.async_api import Browser, async_playwright, Playwright
from app.config import GMAIL, PASS_EVN
from typing import Literal


# making sure credentials are set for type checking purposes, they are 100% set because of check in config.py, otherwise an exception is raised
assert PASS_EVN is not None
assert GMAIL is not None

async def extract_from_evn(browser: Browser):

    # loading the browser and opening the target site
    
    page = await browser.new_page()
    await page.goto("http://efaktura.bg")

    # logging in efaktura with credentials
    await page.locator("#login_username").fill(GMAIL)
    await page.locator("#login_password").fill(PASS_EVN)
    await page.locator("#login_submit").click()

    # navigating to invoice table section
    await page.goto("https://efaktura.bg/index.php")
    await page.wait_for_load_state("networkidle")

    frRight = page.frame(name="frRight")
    assert frRight is not None
    await frRight.goto("https://efaktura.bg/main.php?page=invPrevRecipient")

    # downloading uncollected invoices
    # TODO
