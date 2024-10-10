## Install all requirements using requirements.txt
pip install -r requirements.txt

## Installation of Crawl4AI for webscraping

Using pip 🐍
Choose the installation option that best fits your needs:

Basic Installation
For basic web crawling and scraping tasks:

pip install crawl4ai # This is already included in requirements.txt, this can be skipped

By default, this will install the asynchronous version of Crawl4AI.

**Playwright need to be installed separtely using below methods. The second method has proven to be more reliable in some cases.**

1. Through the command line:

playwright install

2. If the above doesn't work, try this more specific command:

python -m playwright install chromium
