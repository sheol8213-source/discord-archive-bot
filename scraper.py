import json
import os
import requests
from bs4 import BeautifulSoup

URL = "https://yokai.com/"

response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

entries = []

for item in soup.find_all("a"):
    link = item.get("href")
    name = item.text.strip()

    if link and name:
        entries.append({
            "name": name,
            "link": "https://yokai.com" + link
        })

with open("folklore.json", "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2, ensure_ascii=False)
