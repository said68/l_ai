from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import logging

# Configurer les logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    """Configure et retourne un WebDriver en mode sans tête."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def fetch_google_search_results(query):
    """Effectue une recherche Google et retourne les 3 premiers résultats."""
    results = []
    driver = setup_driver()
    try:
        for page in range(1, 3):
            url = f"http://www.google.com/search?q={query}&start={(page - 1) * 10}"
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            search = soup.find_all("div", class_="tF2Cxc", limit=10)

            for h in search:
                title = h.find('h3').text if h.find('h3') else 'No Title'
                link = h.find('a', href=True)['href']
                results.append({"title": title, "url": link, "domain": urlparse(link).netloc})

                if len(results) >= 3:
                    break
            if len(results) >= 3:
                break

    except WebDriverException as e:
        logging.error(f"WebDriver error: {e}")
    finally:
        driver.quit()
    return results[:3]

def get_summary_from_url(url):
    """Récupère et retourne un résumé simplifié du contenu de l'URL spécifiée."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = ' '.join([p.text for p in soup.find_all('p')])
        return text[:500]  # Retourne les 500 premiers caractères pour simplifier
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve content from {url}: {e}")
        return "Failed to retrieve content"

# Exemple d'utilisation
if __name__ == "__main__":
    query = "example query"
    search_results = fetch_google_search_results(query)
    for result in search_results:
        logging.info(result)
        summary = get_summary_from_url(result['url'])
        logging.info(f"Summary for {result['url']}: {summary}")
