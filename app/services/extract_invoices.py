import time
from playwright.async_api import Browser, async_playwright, Playwright
from ..config import platforms_gmail, passwordEVN
from typing import Literal


# making sure credentials are set for type checking purposes, they are 100% set because of check in config.py, otherwise an exception is raised
assert passwordEVN is not None
assert platforms_gmail is not None

async def extract_from_evn(browser: Browser):

    # loading the browser and opening the target site
    
    page = await browser.new_page()
    await page.goto("http://efaktura.bg")

    # logging in efaktura with credentials
    await page.locator("#login_username").fill(platforms_gmail)
    await page.locator("#login_password").fill(passwordEVN)
    await page.locator("#login_submit").click()

    # navigating to invoice table section
    await page.goto("https://efaktura.bg/index.php")
    await page.wait_for_load_state("networkidle")

    frRight = page.frame(name="frRight")
    assert frRight is not None
    await frRight.goto("https://efaktura.bg/main.php?page=invPrevRecipient")

    # downloading uncollected invoices
    # TODO


async def extract_from_vik(browser: Browser):
    pass


async def extract_invoices(playwright: Playwright, platform: Literal["VIK", "EVN"]):
    async with async_playwright() as playwright:

        chromium = playwright.chromium
        browser = await chromium.launch(headless=False)

        match (platform):
            case 'EVN':
                await extract_from_evn(browser)

            case 'VIK':
                await extract_from_vik(browser)

        
        time.sleep(3)
        await browser.close()
        
