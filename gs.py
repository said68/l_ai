from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

# Configurer les logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_google_web_automation(query):
    results = []
    try:
        # Options de Chrome pour exécuter en mode sans tête
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Initialisation de WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # Récupérer les résultats sur les 2 premières pages
        for page in range(1, 3):
            url = f"http://www.google.com/search?q={query}&start={(page - 1) * 10}"
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            search = soup.find_all("div", class_="yuRUbf")

            for rank, h in enumerate(search, start=1 + (page - 1) * 10):
                title = h.find('h3').text if h.find('h3') else 'No Title'
                link = h.a['href'] if h.a else 'No Link'
                results.append({"title": title, "url": link, "domain": urlparse(link).netloc, "rank": rank})

        driver.quit()
    except WebDriverException as e:
        logging.error(f"WebDriver error: {e}")
        driver.quit()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if 'driver' in locals():
            driver.quit()

    return results[:3]  # Retourner les 3 premiers résultats pour la simplicité

# Exemple d'utilisation
if __name__ == "__main__":
    query = "example query"
    search_results = search_google_web_automation(query)
    for result in search_results:
        logging.info(result)
