import sys
import json
import asyncio
import os
from playwright.async_api import async_playwright
from datetime import datetime

# --- CONFIGURATION ---
HEADLESS = True 

async def scrape_tweet(url):
    # Locate the cookies file in the same directory as this script
    cookie_file = os.path.join(os.path.dirname(__file__), "cookies.json")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        
        # Create a blank context first
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )

        # LOAD COOKIES (The Magic Step)
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, 'r') as f:
                    cookies = json.load(f)
                    # Filter cookies to ensure they match the domain (optional but safer)
                    await context.add_cookies(cookies)
                # print("DEBUG: Cookies loaded successfully", file=sys.stderr)
            except Exception as e:
                # If cookie loading fails, we print to stderr so it doesn't break the JSON output
                print(f"Warning: Could not load cookies: {e}", file=sys.stderr)
        else:
            print("Warning: cookies.json not found. Running as guest.", file=sys.stderr)
        
        page = await context.new_page()

        try:
            await page.goto(url, timeout=15000, wait_until='domcontentloaded')
            
            # Wait for content
            await page.wait_for_selector('[data-testid="tweetText"]', timeout=60000)

            # Extract Data
            text_element = await page.query_selector('[data-testid="tweetText"]')
            text = await text_element.inner_text() if text_element else "No text found"

            user_element = await page.query_selector('[data-testid="User-Name"]')
            author = await user_element.inner_text() if user_element else "Unknown Author"

            time_element = await page.query_selector('time')
            timestamp = await time_element.get_attribute('datetime') if time_element else datetime.now().isoformat()

            result = {
                "status": "success",
                "url": url,
                "author": author.replace("\n", " "),
                "content": text,
                "timestamp": timestamp,
                "scraped_at": datetime.now().isoformat()
            }

            print(json.dumps(result))

        except Exception as e:
            error_result = {
                "status": "error",
                "message": str(e),
                "url": url
            }
            print(json.dumps(error_result))

        finally:
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No URL provided"}))
        sys.exit(1)
        
    url_to_scrape = sys.argv[1]
    asyncio.run(scrape_tweet(url_to_scrape))
