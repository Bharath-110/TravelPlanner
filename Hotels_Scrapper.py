import asyncio
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import json

async def main():
    # Define the query parameters for Booking.com
    destination = "vietnam"
    checkin_date = "2024-10-16"
    checkout_date = "2024-10-19"
    group_adults = 2
    no_rooms = 1
    group_children = 1
    child_age = 10

    async with AsyncWebCrawler(verbose=True) as crawler:
        js_code = ["const loadMoreButton = Array.from(document.querySelectorAll('button')).find(button => button.textContent.includes('Load More')); loadMoreButton && loadMoreButton.click();"]
        result = await crawler.arun(
            url=f"https://www.booking.com/searchresults.html?ss={destination}&checkin={checkin_date}&checkout={checkout_date}&group_adults={group_adults}&no_rooms={no_rooms}&group_children={group_children}&age={child_age}",
            js_code=js_code,
            css_selector="",
            bypass_cache=True
        )
        
        # Parse Booking.com results
        soup = BeautifulSoup(result.html, 'html.parser')

        # Find all property cards
        property_cards = soup.find_all('div', {'data-testid': 'property-card'})

        hotels = []

        for card in property_cards:
            # Extract hotel name
            hotel_name = card.find('div', {'data-testid': 'title'}).get_text(strip=True) if card.find('div', {'data-testid': 'title'}) else None

            # Extract location
            location = card.find('span', {'data-testid': 'address'}).get_text(strip=True) if card.find('span', {'data-testid': 'address'}) else None

            # Extract distance from center
            distance = card.find('span', {'data-testid': 'distance'}).get_text(strip=True) if card.find('span', {'data-testid': 'distance'}) else None

            # Extract review score
            review_score_div = card.find('div', {'data-testid': 'review-score'})
            review_score = review_score_div.find('div', class_='ac4a7896c7').get_text(strip=True).replace('Scored', '').strip() if review_score_div else None
            review_rating = review_score_div.find('div', class_='cb2cbb3ccb').get_text(strip=True) if review_score_div else None
            reviews = review_score_div.find('div', class_='abf093bdfe').get_text(strip=True) if review_score_div else None

            hotels.append({
                'hotel_name': hotel_name,
                'location': location,
                'distance': distance,
                'review_score': review_score,
                'review_rating': review_rating,
                'reviews': reviews
            })

        # Convert the list of hotels to JSON
        hotels_json = json.dumps(hotels, indent=4, ensure_ascii=False)

        # Print the JSON
        print(hotels_json)

if __name__ == "__main__":
    asyncio.run(main())