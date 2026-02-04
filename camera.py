import asyncio
import json
import os
from playwright.async_api import async_playwright

async def take_photo():
    async with async_playwright() as p:
        # Launch browser (Headless=True means invisible)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Load Cookies
        cookie_path = os.path.expanduser("~/.openclaw/skills/x-stealth/cookies.json")
        if os.path.exists(cookie_path):
            with open(cookie_path, 'r') as f:
                cookies = json.load(f)
                # Fix sameSite issue if present
                for c in cookies:
                    if 'sameSite' in c: del c['sameSite']
                    if 'storeId' in c: del c['storeId']
                await context.add_cookies(cookies)
            print("✅ Cookies loaded.")
        else:
            print("⚠️ No cookies found!")

        page = await context.new_page()
        
        print("📸 Going to X.com...")
        try:
            await page.goto("https://x.com/home", timeout=60000)
            await page.wait_for_timeout(5000) # Wait 5s for page to settle
        except:
            print("⚠️ Page load timed out, taking photo anyway...")

        # Take the picture
        await page.screenshot(path="evidence.png", full_page=True)
        print("✅ Photo taken: evidence.png")
        await browser.close()

asyncio.run(take_photo())
