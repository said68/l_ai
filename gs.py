import asyncio
from bs4 import BeautifulSoup
from pyppeteer import launch

async def fetch_url(url):
    """Launches a headless browser and fetches the page content for the given URL."""
    browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    page = await browser.newPage()
    await page.goto(url)
    content = await page.content()
    await browser.close()
    return content

async def get_google_search_results(query):
    """Performs a Google search and returns the first three result URLs."""
    search_url = f"https://www.google.com/search?q={query}"
    content = await fetch_url(search_url)
    soup = BeautifulSoup(content, 'html.parser')
    results = []
    for item in soup.select('.tF2Cxc')[:3]:
        url = item.find('a')['href']
        results.append(url)
    return results

# Example usage:
async def main():
    query = "your_search_query_here"
    search_results = await get_google_search_results(query)
    print("Search Results:")
    for url in search_results:
        print(url)

if __name__ == "__main__":
    asyncio.run(main())
