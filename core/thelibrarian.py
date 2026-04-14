from pathlib import Path
import os
import re
import json
from gemini_tools import web_fetch

class FatCatsArchive:
    def __init__(self, storage_dir="./.cache/fatcats"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name):
        """Sanitizes a string to be used as a filename."""
        name = re.sub(r'[^a-zA-Z0-9_.-]', '_', name)
        return name[:100] # Limit filename length

    def has(self, q):
        filename = self._sanitize_filename(q)
        return (self.storage_dir / filename).exists()

    def retrieve(self, q):
        filename = self._sanitize_filename(q)
        filepath = self.storage_dir / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None

    def store(self, q, d):
        filename = self._sanitize_filename(q)
        filepath = self.storage_dir / filename
        with open(filepath, 'w') as f:
            json.dump(d, f)

class HeadlessBrowser:
    def fetch_deep(self, q, depth=3):
        # Assuming q is a URL for now
        url = q
        try:
            content = web_fetch.fetch(prompt=f"Summarize the content of the URL {url}")
            return content
        except Exception as e:
            return f"Failed to fetch {url}: {e}"

    def extract_main_content(self, html):
        # The web_fetch tool with summarize prompt already returns extracted content
        return html

def summarize_vectors(text):
    # This is a mock from the original code.
    # In a real implementation, this would involve a proper NLP library.
    return {"summary": text[:1000], "vectors": [len(text)]}

class TheLibrarian:
    def __init__(self, bandwidth_mode="AUTO"):
        self.cache = FatCatsArchive()
        self.scraper = HeadlessBrowser()

    def check_connection_speed(self):
        # Mock implementation
        return "STRONG"

    def research_topic(self, q):
        if self.cache.has(q):
            print(f"Librarian: Found '{q}' in cache.")
            return self.cache.retrieve(q)

        print(f"Librarian: Researching '{q}' on the web...")
        raw_content = self.scraper.fetch_deep(q)

        if isinstance(raw_content, str) and raw_content.startswith("Failed to fetch"):
            print(f"Librarian: Error - {raw_content}")
            return {"error": raw_content}

        print("Librarian: Distilling information...")
        clean_content = self.distill_information(raw_content)

        print("Librarian: Storing result in cache.")
        self.cache.store(q, clean_content)
        return clean_content

    def distill_information(self, html):
        main_content = self.scraper.extract_main_content(html)
        return summarize_vectors(main_content)
