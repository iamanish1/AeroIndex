from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})

    page.goto(
        "https://www.google.com/travel/flights",
        wait_until="domcontentloaded",
        timeout=60000,
    )
    page.wait_for_timeout(4000)

    origin = page.locator('input[aria-label="Where from?"]:visible').first

    origin.click()
    origin.press("ControlOrMeta+A")
    origin.fill("Delhi")
    page.wait_for_timeout(2500)

    print("\n--- VISIBLE OPTIONS ---")

    options = page.locator('[role="option"]:visible')
    for i in range(options.count()):
        option = options.nth(i)
        print(
            i,
            "TEXT:", repr(option.inner_text()),
            "ARIA:", option.get_attribute("aria-label"),
        )

    print("\n--- VISIBLE TEXT AROUND SEARCH ---")
    print(page.locator("body").inner_text()[:2500])

    page.wait_for_timeout(10000)
    browser.close()
