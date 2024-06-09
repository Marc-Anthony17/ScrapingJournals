import json
import asyncio
from playwright.async_api import async_playwright
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CHECKPOINT_FILE = 'checkpoint.txt'

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r', encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def save_checkpoint(url):
    with open(CHECKPOINT_FILE, 'a', encoding="utf-8") as f:
        f.write(url + '\n')

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

async def main(urls, max_concurrent_tasks=8):
    # Create a directory for the output if it doesn't exist
    if not os.path.exists('html'):
        os.makedirs('html')

    # Load checkpoint
    completed_urls = load_checkpoint()

    semaphore = asyncio.Semaphore(max_concurrent_tasks)
    
    tasks = []
    for url in urls:
        if url in completed_urls:
            logging.info(f'Skipping {url} as it is already processed')
            continue
        task = asyncio.create_task(fetch_page_content(url, semaphore))
        tasks.append((url, task))
    
    for i, (url, task) in enumerate(asyncio.as_completed([task for url, task in tasks])):
        content = await task
        if content:
            with open(f'html/output_{i}.html', 'w', encoding="utf-8") as f:
                f.write(content)
            save_checkpoint(url)
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
