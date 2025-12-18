import requests
import csv
import time
import logging
import re
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log', mode='a'),
        logging.StreamHandler()
    ]
)

class YGOScraper:
    def __init__(self):
        self.base_url = "https://ygoprodeck.com/api/elastic/card_search.php"
        self.session = requests.Session()
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.8',
            'priority': 'u=1, i',
            'referer': 'https://ygoprodeck.com/card-database/?num=100&offset=0',
            'sec-ch-ua': '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        self.session.headers.update(self.headers)
        self.cards_data = []

    def make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic"""
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = self.session.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                logging.info(f"Successfully fetched page with params: {params}")
                return data

            except requests.exceptions.RequestException as e:
                logging.warning(f"Attempt {attempt + 1} failed for params {params}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logging.error(f"All attempts failed for params {params}")
                    raise

    def scrape_page(self, offset: int) -> List[Dict[str, Any]]:
        """Scrape a single page of cards"""
        params = {
            'num': 100,
            'offset': offset
        }

        try:
            data = self.make_request(params)

            # Extract cards from response
            if 'data' in data:
                cards = data['data']
            elif 'cards' in data:
                cards = data['cards']
            else:
                logging.warning(f"No 'data' or 'cards' field found in response for offset {offset}")
                cards = []

            logging.info(f"Found {len(cards)} cards on page with offset {offset}")
            return cards

        except Exception as e:
            logging.error(f"Error scraping page with offset {offset}: {e}")
            return []

    def clean_text_field(self, text: str) -> str:
        """Clean text fields to remove problematic characters"""
        if not text:
            return ""

        # Replace newlines, tabs, and carriage returns with spaces
        text = re.sub(r'[\r\n\t]', ' ', str(text))

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        # Escape quotes to prevent CSV issues
        text = text.replace('"', '""')

        return text

    def flatten_card_data(self, card: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested card data for CSV storage"""
        flattened = {}

        # Basic card info with cleaned text
        flattened['id'] = str(card.get('id', ''))
        flattened['name'] = self.clean_text_field(card.get('name', ''))
        flattened['type'] = self.clean_text_field(card.get('type', ''))
        flattened['desc'] = self.clean_text_field(card.get('desc', ''))

        # Monster stats (if applicable)
        flattened['atk'] = str(card.get('atk', ''))
        flattened['def'] = str(card.get('def', ''))
        flattened['level'] = str(card.get('level', ''))
        flattened['rank'] = str(card.get('rank', ''))
        flattened['linkval'] = str(card.get('linkval', ''))

        # Card properties with cleaned text
        flattened['race'] = self.clean_text_field(card.get('race', ''))
        flattened['attribute'] = self.clean_text_field(card.get('attribute', ''))
        flattened['archetype'] = self.clean_text_field(card.get('archetype', ''))

        # Pricing information
        card_prices = card.get('card_prices', [])
        if card_prices and len(card_prices) > 0:
            flattened['cardmarket_price'] = str(card_prices[0].get('cardmarket_price', ''))
            flattened['tcgplayer_price'] = str(card_prices[0].get('tcgplayer_price', ''))
            flattened['amazon_price'] = str(card_prices[0].get('amazon_price', ''))
            flattened['coolstuffinc_price'] = str(card_prices[0].get('coolstuffinc_price', ''))
        else:
            flattened.update({
                'cardmarket_price': '',
                'tcgplayer_price': '',
                'amazon_price': '',
                'coolstuffinc_price': ''
            })

        # Card images
        card_images = card.get('card_images', [])
        if card_images and len(card_images) > 0:
            flattened['image_url'] = str(card_images[0].get('image_url', ''))
            flattened['image_url_small'] = str(card_images[0].get('image_url_small', ''))
        else:
            flattened.update({
                'image_url': '',
                'image_url_small': ''
            })

        return flattened

    def scrape_all_cards(self) -> List[Dict[str, Any]]:
        """Scrape ALL Yu-Gi-Oh! cards by continuing until API returns empty"""
        all_cards = []
        offset = 0
        batch_size = 100
        page_number = 1

        while True:
            logging.info(f"Scraping page {page_number} (offset: {offset})")

            cards = self.scrape_page(offset)
            if not cards:
                logging.info(f"No more cards found at offset {offset}. Scraping complete.")
                break

            all_cards.extend(cards)
            offset += batch_size
            page_number += 1

            # Rate limiting - respect API limits
            time.sleep(1)

            # Progress update every 10 pages
            if page_number % 10 == 0:
                logging.info(f"Collected {len(all_cards)} cards so far...")

        logging.info(f"Total cards scraped: {len(all_cards)}")
        return all_cards

    def scrape_multiple_pages(self, num_pages: int = 5) -> List[Dict[str, Any]]:
        """Scrape specified number of pages of cards"""
        all_cards = []

        for page in range(num_pages):
            offset = page * 100
            logging.info(f"Scraping page {page + 1}/{num_pages} (offset: {offset})")

            cards = self.scrape_page(offset)
            if cards:
                all_cards.extend(cards)
            else:
                logging.warning(f"No cards found on page {page + 1}")
                break  # Stop early if no cards found

            # Rate limiting - wait between requests
            time.sleep(1)

        logging.info(f"Total cards scraped: {len(all_cards)}")
        return all_cards

    def validate_card_record(self, card: Dict[str, Any], expected_fields: int = 18) -> bool:
        """Validate that a card record has the correct number of fields"""
        if len(card) != expected_fields:
            logging.warning(f"Card record has {len(card)} fields, expected {expected_fields}: {card.get('name', 'Unknown')}")
            return False
        return True

    def save_to_csv(self, cards: List[Dict[str, Any]], filename: str = 'data/yugioh_cards.csv'):
        """Save card data to CSV file with validation and proper formatting"""
        if not cards:
            logging.warning("No cards to save")
            return

        # Flatten all cards
        flattened_cards = [self.flatten_card_data(card) for card in cards]

        # Define CSV headers
        headers = [
            'id', 'name', 'type', 'desc', 'atk', 'def', 'level', 'rank', 'linkval',
            'race', 'attribute', 'archetype',
            'cardmarket_price', 'tcgplayer_price', 'amazon_price', 'coolstuffinc_price',
            'image_url', 'image_url_small'
        ]

        # Validate all cards before writing
        valid_cards = []
        invalid_count = 0

        for card in flattened_cards:
            if self.validate_card_record(card, len(headers)):
                valid_cards.append(card)
            else:
                invalid_count += 1
                logging.warning(f"Skipping invalid card record: {card.get('name', 'Unknown')}")

        if invalid_count > 0:
            logging.warning(f"Skipped {invalid_count} invalid card records due to field count mismatch")

        if not valid_cards:
            logging.error("No valid cards to save after validation")
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Use csv.writer with QUOTE_ALL to ensure proper quoting
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

                # Write header
                writer.writerow(headers)

                # Write card data
                for card in valid_cards:
                    # Ensure the order matches headers
                    row = [card.get(field, '') for field in headers]
                    writer.writerow(row)

            logging.info(f"Successfully saved {len(valid_cards)} cards to {filename} (skipped {invalid_count} invalid)")

        except Exception as e:
            logging.error(f"Error saving to CSV: {e}")
            raise

    def run(self, num_pages: int = 5):
        """Run the complete scraping process"""
        logging.info("Starting Yu-Gi-Oh! card scraping process")

        try:
            if num_pages is None:
                # Scrape ALL cards
                cards = self.scrape_all_cards()
            else:
                # Scrape specified number of pages
                cards = self.scrape_multiple_pages(num_pages)

            if cards:
                # Save to CSV
                self.save_to_csv(cards)
                logging.info("Scraping completed successfully")
            else:
                logging.error("No cards were scraped")

        except Exception as e:
            logging.error(f"Scraping process failed: {e}")
            raise

def main():
    """Main function to run the scraper"""
    import argparse

    parser = argparse.ArgumentParser(description='Yu-Gi-Oh! Card Scraper')
    parser.add_argument('--pages', type=int, help='Number of pages to scrape (default: 5)')
    parser.add_argument('--all', action='store_true', help='Scrape ALL available cards')

    args = parser.parse_args()

    scraper = YGOScraper()

    if args.all:
        print("🃏 Scraping ALL Yu-Gi-Oh! cards...")
        scraper.run(num_pages=None)  # Explicitly pass None for scraping all cards
    elif args.pages:
        print(f"🃏 Scraping {args.pages} pages...")
        scraper.run(num_pages=args.pages)
    else:
        print("🃏 Scraping default 5 pages...")
        scraper.run()  # Default behavior

if __name__ == "__main__":
    main()