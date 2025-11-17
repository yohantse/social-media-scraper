from playwright.sync_api import sync_playwright


def scrape_tiktok(url, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
    page = browser.new_page()
    page.goto(url)
    # TODO: Add scraping logic
    data = {'url': url}
    browser.close()
    return data