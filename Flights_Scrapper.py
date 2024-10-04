from bs4 import BeautifulSoup
import json
import asyncio
from crawl4ai import AsyncWebCrawler

async def scrape_flights(src, des, ddate, rdate, adult, child, infant):
    # Construct the Bing flights search URL
    bing_url = (
        f"https://www.bing.com/travel/flight-search?q=flights+from+{src}-{des}&src={src}&des={des}&ddate={ddate}&isr=1&rdate={rdate}&cls=0&adult={adult}&child={child}&infant={infant}"
    )

    async with AsyncWebCrawler(verbose=True) as crawler:
        # Crawl Bing
        bing_js_code = ["const loadMoreButton = Array.from(document.querySelectorAll('button')).find(button => button.textContent.includes('Load More')); loadMoreButton && loadMoreButton.click();"]
        bing_result = await crawler.arun(
            url=bing_url,
            js_code=bing_js_code,
            css_selector="",
            bypass_cache=True
        )

        # Parse Bing results
        bing_soup = BeautifulSoup(bing_result.html, 'html.parser')

        # Find all flight listings
        flight_listings = bing_soup.find_all('div', {'class': 'itrCard itrSummaryCard fbPreventScroll'})

        flights = []

        for listing in flight_listings:
            # Extract flight details
            airline_name_divs = listing.find('div', {'class': 'itrTxtPair airlinePair'}).find_all('div', {'class': 'bt_focusText'})
            airline_name = airline_name_divs[-1].find_all('div')[-1].get_text(strip=True) if airline_name_divs else None
            departure_arrival = listing.find('div', {'class': 'itrTxtPair airlinePair'}).find('span').get_text(strip=True) if listing.find('div', {'class': 'itrTxtPair airlinePair'}) else None
            departure_time = listing.find('div', {'class': 'itrTxtPair durationPair'}).find('span').get_text(strip=True) if listing.find('div', {'class': 'itrTxtPair durationPair'}) else None
            journey_duration = listing.find('div', {'class': 'itrTxtPair durationPair'}).find_all('span')[1].get_text(strip=True) if listing.find('div', {'class': 'itrTxtPair durationPair'}) else None
            price_span = listing.find('div', {'class': 'itrTxtPair pricePair'}).find('span', {'class': 'itrPriceVal'})
            if price_span:
                currency = price_span.get('title', '').strip()
                price_value = price_span.find_all('div')[-1].get_text(strip=True)
                price = f"{currency} {price_value}"
            else:
                price = None
            flights.append({
                'airline_name': airline_name,
                'departure_arrival': departure_arrival,
                'departure_time': departure_time,
                'journey_duration': journey_duration,
                'price': price
            })

        # Convert the list of flights to JSON
        flights_json = json.dumps(flights, indent=4, ensure_ascii=False)

        # Print the JSON
        print(flights_json)

if __name__ == "__main__":
    # Define the query parameters for Bing flights search
    src = "sin"
    des = "blr"
    ddate = "2024-10-18"
    rdate = "2024-10-25"
    adult = 2
    child = 0
    infant = 0

    asyncio.run(scrape_flights(src, des, ddate, rdate, adult, child, infant))