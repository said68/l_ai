import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup

async def fetch_url(url):
    """Launches a headless browser and fetches the page content for the given URL."""
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    page = await browser.newPage()
    await page.goto(url)
    content = await page.content()
    await browser.close()
    return content

def get_google_search_results(query):
    """Perform a Google search and return the first three result URLs."""
    search_url = f"https://www.google.com/search?q={query}"
    # This runs our async function in a sync manner for simplicity in integration
    content = asyncio.get_event_loop().run_until_complete(fetch_url(search_url))
    soup = BeautifulSoup(content, 'html.parser')
    results = []
    for item in soup.select('.tF2Cxc')[:3]:  # We limit to the first 3 results
        title = item.select_one('h3').text if item.select_one('h3') else 'No title'
        link = item.select_one('a')['href']
        results.append({'title': title, 'url': link})
    return results

def get_summary_from_url(url):
    """Fetch the URL content and return a simple summary (first 500 characters)."""
    content = asyncio.get_event_loop().run_until_complete(fetch_url(url))
    soup = BeautifulSoup(content, 'html.parser')
    text = ' '.join(p.text for p in soup.find_all('p'))
    return text[:500]  # Return the first 500 characters as a summary
