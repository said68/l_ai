import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def fetch_url(url):
    try:
        browser = await launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-zygote',
                '--single-process',  # May be necessary in Docker or cloud environments
            ],
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False,
            autoClose=True,  # Ensure browser closes properly on script completion
            dumpio=True  # Enable logging for Chromium process for diagnostics
        )
        page = await browser.newPage()
        await page.goto(url, {'timeout': 60000})  # Extended timeout for loading the page
        content = await page.content()
        await browser.close()
        return content
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def get_google_search_results(query):
    search_url = f"https://www.google.com/search?q={query}"
    loop = asyncio.get_event_loop()
    content = loop.run_until_complete(fetch_url(search_url))
    if not content:
        return []  # Return an empty list if no content was fetched
    soup = BeautifulSoup(content, 'html.parser')
    results = []
    for item in soup.select('.tF2Cxc')[:3]:  # Limit to the first 3 results
        title = item.select_one('h3').text if item.select_one('h3') else 'No title'
        link = item.select_one('a')['href']
        results.append({'title': title, 'url': link})
    return results

def get_summary_from_url(url):
    """Fetch the URL content and return a simple summary (first 500 characters)."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    content = loop.run_until_complete(fetch_url(url))
    soup = BeautifulSoup(content, 'html.parser')
    text = ' '.join(p.text for p in soup.find_all('p'))
    return text[:500]  # Return the first 500 characters as a summary
