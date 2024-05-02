from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Spécifiez explicitement la version du ChromeDriver si nécessaire
    driver = webdriver.Chrome(service=Service(ChromeDriverManager(version="95.0.4638.69").install()), options=chrome_options)
    return driver

def search_google_web_automation(query):
    """Effectue une recherche Google et extrait les trois premiers résultats."""
    driver = setup_driver()
    results = []
    try:
        driver.get(f"https://www.google.com/search?q={query}")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        search_items = soup.find_all('div', class_='tF2Cxc', limit=3)

        for item in search_items:
            title = item.find('h3').text if item.find('h3') else 'No Title'
            link = item.find('a')['href']
            results.append({"title": title, "url": link})
    except Exception as e:
        logging.error(f"Error during web search: {e}")
    finally:
        driver.quit()
    return results

def get_summary_from_url(url):
    """Extrait un résumé du contenu de l'URL spécifiée."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join(p.text for p in soup.find_all('p'))
        return text[:500]  # Retourne les 500 premiers caractères pour simplifier
    except Exception as e:
        logging.error(f"Error fetching summary from {url}: {e}")
        return "Failed to retrieve content"
