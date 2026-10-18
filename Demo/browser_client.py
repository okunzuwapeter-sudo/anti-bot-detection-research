#!/usr/bin/env python3
"""
Open the local observer endpoint in Chromium using Playwright.

Start observer.py first. This script navigates only to the local loopback
server at 127.0.0.1; it does not visit or automate a public website.
"""

from playwright.sync_api import sync_playwright


URL = "http://127.0.0.1:8080/demo?source=playwright"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            response = page.goto(URL, wait_until="domcontentloaded", timeout=10_000)

            print("Status:", response.status if response else "No main response")
            print("Page title:", page.title())
            print("Response body:")
            print(page.locator("body").inner_text())
        finally:
            browser.close()


if __name__ == "__main__":
    main()

