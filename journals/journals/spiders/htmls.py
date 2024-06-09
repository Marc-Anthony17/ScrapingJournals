import json
import os
import logging
import concurrent.futures
from playwright.sync_api import sync_playwright
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CHECKPOINT_FILE = 'checkpoint.txt'
OUTPUT_DIR = 'html'
LOCK = threading.Lock()

def load_checkpoint():
    """Load the set of completed URLs from the checkpoint file."""
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r', encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def save_checkpoint(url):
    """Save a completed URL to the checkpoint file."""
    with LOCK:
        with open(CHECKPOINT_FILE, 'a', encoding="utf-8") as f:
            f.write(f"{url}\n")

def fetch_page_content(url, retries=3, timeout=30):
    """Fetch the content of the page at the given URL."""
    for attempt in range(1, retries + 1):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=timeout * 1000)  # Timeout in milliseconds
                # Wait for the necessary content to load
                page.wait_for_selector('.article-text')
                content = page.content()
                browser.close()
                return content
        except Exception as e:
            logging.error(f'Error fetching {url} on attempt {attempt}: {e}')
            if attempt == retries:
                logging.error(f'Failed to fetch {url} after {retries} attempts')
                return None

def save_content(i, url, content):
    """Save the content to a file."""
    if content:
        output_path = os.path.join(OUTPUT_DIR, f'output_{i}.html')
        with open(output_path, 'w', encoding="utf-8") as f:
            f.write(content)
        save_checkpoint(url)
        logging.info(f'Completed {i+1}: {url}')
    else:
        logging.warning(f'Skipped {i+1} due to errors: {url}')

def process_url(i, url):
    """Process a single URL."""
    content = fetch_page_content(url)
    save_content(i, url, content)

def main(urls):
    """Main function to process URLs."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    completed_urls = load_checkpoint()

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(process_url, i, url): url for i, url in enumerate(urls) if url not in completed_urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f'Error processing {url}: {e}')

if __name__ == "__main__":
    with open("firstset.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract URLs from the JSON data
    urls = [i["journal_url"] for i in data][:42699]

    # Run the main function
    main(urls)