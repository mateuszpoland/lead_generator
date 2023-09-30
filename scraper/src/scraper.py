import requests
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv
from typing import Type
import json
import json

browserless_api_key = os.getenv("BROWSERLESS_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

class Scraper:
    def scrape_website(url: str) -> str:
        print(f"scraping {url} content".format(url))
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
        }

        payload = json.dumps({"url": url})
        post_url = f"https://chrome.browserless.io/content?token={browserless_api_key}"
        response = requests.post(post_url, headers=headers, data=payload)
        if response.status_code != 200:
            return (f"HTTP request failed with status code {response.status_code}")

        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        print(f"Text: {text} content".format(text))

        return text

    @staticmethod
    def extract_emails(text: str) -> str:
        email_pattern = r"[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"
        emails = re.findall(email_pattern, text)

        # Return only unique emails
        return list(set(emails))