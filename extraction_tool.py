import requests
from bs4 import BeautifulSoup
import re
import spacy
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun, WikipediaAPIWrapper
from langchain.tools import BaseTool
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 1. Web Search Tool
search = DuckDuckGoSearchRun()

# 2. Wikipedia Tool
wikipedia_api = WikipediaAPIWrapper()
wikipedia = WikipediaQueryRun(api_wrapper=wikipedia_api)

# 3. Custom Web Scraping Tool for Hotels
class HotelInfoScraper(BaseTool):
    name = "HotelInfoScraper"
    description = "Scrapes hotel information from a travel website"

    def _run(self, location: str) -> str:
        url = f"https://www.booking.com/searchresults.html?ss={location}"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        # Retry mechanism
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        try:
            response = session.get(url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses
            soup = BeautifulSoup(response.content, 'html.parser')
            hotels = soup.find_all('div', {'data-testid': 'property-card'})
            results = []
            for hotel in hotels[:5]:  # Limit to first 5 results
                name = hotel.find('div', {'data-testid': 'title'}).text.strip()
                price = hotel.find('span', {'data-testid': 'price-and-discounted-price'}).text.strip()
                results.append(f"{name}: {price}")
            return "\n".join(results)
        except requests.exceptions.RequestException as e:
            return f"Error fetching hotel information: {e}"

# 4. Custom Web Scraping Tool for Flights
class FlightInfoScraper(BaseTool):
    name = "FlightInfoScraper"
    description = "Scrapes flight information from a travel website"

    def _run(self, route: str) -> str:
        origin, destination = route.split(' to ')
        url = f"https://www.kayak.com/flights/{origin}-{destination}/2023-12-01"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        # Retry mechanism
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        try:
            response = session.get(url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses
            soup = BeautifulSoup(response.content, 'html.parser')
            flights = soup.find_all('div', class_='inner-grid keel-grid')
            results = []
            for flight in flights[:5]:  # Limit to first 5 results
                airline = flight.find('div', {'class': 'bottom', 'dir': 'ltr'}).text.strip()
                price = flight.find('div', {'class': 'price-text'}).text.strip()
                results.append(f"{airline}: {price}")
            return "\n".join(results)
        except requests.exceptions.RequestException as e:
            return f"Error fetching flight information: {e}"

# 5. Natural Language Processing for Information Extraction
nlp = spacy.load("en_core_web_sm")

def extract_travel_info(text):
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
    dates = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
    return f"Locations: {', '.join(locations)}\nDates: {', '.join(dates)}"

# 6. Regular Expressions for Pattern Matching
def extract_flight_info(text):
    flight_pattern = r'([A-Z]{2,3}\d{3,4})'
    matches = re.findall(flight_pattern, text)
    return f"Flight numbers: {', '.join(matches)}"

# Example usage
if __name__ == "__main__":
    hotel_scraper = HotelInfoScraper()
    flight_scraper = FlightInfoScraper()
    
    print("Hotel Information:")
    print(hotel_scraper._run("Paris"))
    
    print("\nFlight Information:")
    print(flight_scraper._run("JFK to LAX"))
    
    print("\nNLP Extraction:")
    text = "I want to travel from New York to London on December 15th"
    print(extract_travel_info(text))
    
    print("\nFlight Number Extraction:")
    text = "My flight AA123 was cancelled, so I was rebooked on UA456"
    print(extract_flight_info(text))