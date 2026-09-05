from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})

    page.goto(
        "https://www.google.com/travel/flights",
        wait_until="domcontentloaded",
        timeout=60000,
    )
    page.wait_for_timeout(5000)

    print("\n--- INPUTS ---")
    for i in range(page.locator("input").count()):
        el = page.locator("input").nth(i)
        print(
            i,
            "placeholder=", el.get_attribute("placeholder"),
            "aria-label=", el.get_attribute("aria-label"),
            "value=", el.input_value(),
        )

    print("\n--- BUTTONS ---")
    for i in range(min(page.locator("button").count(), 80)):
        el = page.locator("button").nth(i)
        try:
            print(
                i,
                "text=", repr(el.inner_text()),
                "aria-label=", el.get_attribute("aria-label"),
            )
        except Exception:
            pass

    page.wait_for_timeout(3000)
    browser.close()
