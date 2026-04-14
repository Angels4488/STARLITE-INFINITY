import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
from core.recorder import Recorder

logger = logging.getLogger(__name__)

class LibrarianV2:
    """
    LIBRARIAN V2: Wide-Scale Internet Intelligence Scraper.
    Treats the entire internet as the AGI's dataset.
    Features: Recursive crawling, content distillation, and memory integration.
    """
    def __init__(self, memory, recorder=None):
        self.memory = memory
        self.recorder = recorder or Recorder()
        self.visited_urls = set()
        self.queue = asyncio.Queue()
        self.max_depth = 5
        self.concurrency_limit = 10
        self.semaphore = asyncio.Semaphore(self.concurrency_limit)

    async def ingest_seed(self, url):
        """Adds a starting point for the intelligence gathering."""
        await self.queue.put((url, 0))
        logger.info(f"Seed URL ingested: {url}")

    async def start_scraping(self):
        """Begins the wide-scale internet exploration."""
        print("\n--- LIBRARIAN V2: INTERNET SCRAPE ENGAGED ---")
        tasks = []
        while not self.queue.empty() or tasks:
            # Launch workers up to concurrency limit
            while len(tasks) < self.concurrency_limit and not self.queue.empty():
                url, depth = await self.queue.get()
                if url not in self.visited_urls and depth <= self.max_depth:
                    self.visited_urls.add(url)
                    task = asyncio.create_task(self.process_url(url, depth))
                    tasks.append(task)
            
            # Wait for any task to complete
            if tasks:
                done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for t in done:
                    try:
                        new_links = await t
                        if new_links:
                            for link in new_links:
                                await self.queue.put(link)
                    except Exception as e:
                        logger.error(f"Scrape error: {e}")
            
            # Slow down for politeness and resource management
            await asyncio.sleep(0.1)

    async def process_url(self, url, depth):
        """Fetches, distills, and stores information from a single page."""
        async with self.semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Distillation Logic
                            text = self.distill_content(soup)
                            if text:
                                # Inject into Mycelium Memory
                                self.memory.add_fact(f"SOURCE[{url}]: {text[:500]}")
                                logger.info(f"Wisdom distilled from {url}")

                            # Discovery Logic
                            if depth < self.max_depth:
                                return self.discover_links(soup, url, depth)
            except Exception as e:
                logger.debug(f"Failed to process {url}: {e}")
        return []

    def distill_content(self, soup):
        """Filters out noise to find the core intelligence."""
        # Remove scripts, styles, etc.
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract meaningful text
        text = soup.get_text(separator=' ')
        # Simple cleanup
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return ' '.join(chunk for chunk in chunks if chunk)

    def discover_links(self, soup, base_url, depth):
        """Finds new pathways for exploration."""
        links = []
        for a in soup.find_all('a', href=True):
            absolute_url = urljoin(base_url, a['href'])
            # Filter for sane links (http/https only)
            if urlparse(absolute_url).scheme in ('http', 'https'):
                links.append((absolute_url, depth + 1))
        return links
