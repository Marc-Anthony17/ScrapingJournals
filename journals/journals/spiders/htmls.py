import json
import asyncio
from playwright.async_api import async_playwright
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_page_content(url, semaphore, retries=3):
    async with semaphore:
        for attempt in range(1, retries + 1):
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)  # Use `chromium`, `firefox`, or `webkit`
                    page = await browser.new_page()
                    await page.goto(url)
                    
                    # Wait for the necessary content to load
                    await page.wait_for_selector('.article-text')
                    
                    content = await page.content()
                    await browser.close()
                    return content
            except Exception as e:
                logging.error(f'Error fetching {url} on attempt {attempt}: {e}')
                if attempt == retries:
                    logging.error(f'Failed to fetch {url} after {retries} attempts')
                    return None

async def main(urls, max_concurrent_tasks=5):
    # Create a directory for the output if it doesn't exist
    if not os.path.exists('html'):
        os.makedirs('html')
    if os.path.exists(f'html/output_{i}.html'):
        return
    semaphore = asyncio.Semaphore(max_concurrent_tasks)
    
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch_page_content(url, semaphore))
        tasks.append(task)
    
    for i, task in enumerate(asyncio.as_completed(tasks)):
        content = await task
        if content:
            with open(f'html/output_{i}.html', 'w', encoding="utf-8") as f:
                f.write(content)
            logging.info(f'Completed {i+1}/{len(urls)}')
        else:
            logging.warning(f'Skipped {i+1}/{len(urls)} due to errors')

if __name__ == "__main__":
    with open("firstset.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract URLs from the JSON data
    urls = [i["journal_url"] for i in data][:42699]

    # Run the main function
    asyncio.run(main(urls))
