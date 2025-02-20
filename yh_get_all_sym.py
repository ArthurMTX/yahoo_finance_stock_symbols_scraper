import requests
import json
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.DEBUG,
    filename='yh_get_all_sym.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BASE_URL = "https://query1.finance.yahoo.com/v1/finance/lookup"
DEFAULT_PARAMS = {
    "type": "all",
    "start": "0",
    "count": "100",
    "formatted": "true",
    "fetchPricingData": "true",
    "lang": "en-US",
    "region": "US",
    "crumb": "O4o6AKsM4xk"
}

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
}

def call_url(query, start=0, count=100):
    """
    Calls the API using the search term, starting position, and number of results.
    In case of an error, it retries after 1 second.
    """
    params = DEFAULT_PARAMS.copy()
    params["query"] = query
    params["start"] = str(start)
    params["count"] = str(count)
    while True:
        try:
            response = requests.get(BASE_URL, headers=HEADERS, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.warning(f"Request failed for query '{query}' (start={start}): {e}")
            print(f"Request failed for query '{query}' (start={start}): {e}. Retrying in 1 sec...")
            time.sleep(1)

def get_total_count(data, query):
    """
    Extracts the total number of results available for the search term.
    [Example: For "A", the 'lookupTotals' key might return "all": 10000]
    """
    try:
        result = data.get("finance", {}).get("result", [])
        if not result:
            logging.info(f"No results for query '{query}'")
            return 0
        lookup_totals = result[0].get("lookupTotals", {})
        total = lookup_totals.get("all", 0)
        logging.info(f"Total count for query '{query}': {total}")
        return int(total)
    except Exception as e:
        logging.error(f"Error extracting total count for '{query}': {e}")
        return 0

def update_file(yh_all_sym, filename="yh_all_symbols.txt"):
    """
    Saves the dictionary of symbols into a JSON file.
    """
    with open(filename, "w", encoding="UTF-8") as f:
        json.dump(yh_all_sym, f, indent=2)
    print(f"Updated file with {len(yh_all_sym)} symbols.")

def process_block(query, yh_all_sym, lock, count=100):
    """
    Iterates over the result pages for the given search term.
    Updates the shared dictionary.
    """
    start = 0
    while True:
        print(f"Processing query '{query}' starting at {start}")
        logging.info(f"Processing query '{query}' starting at {start}")
        data = call_url(query, start, count)
        result = data.get("finance", {}).get("result", [])
        if not result or not result[0].get("documents"):
            break
        docs = result[0].get("documents", [])
        if not docs:
            break
        with lock:
            for doc in docs:
                symbol = doc.get("symbol")
                shortName = doc.get("shortName", "")
                if symbol:
                    yh_all_sym[symbol] = shortName
        if len(docs) < count:
            break
        start += count

def main():
    # Create the search set: A-Z and 0-9
    search_set = [chr(x) for x in range(65, 91)] + [chr(x) for x in range(48, 58)]
    yh_all_sym = {}
    lock = threading.Lock()
    threshold = 9000
    tasks = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Search for single letters
        for term in search_set:
            print(f"Querying single letter: '{term}'")
            data = call_url(term, 0, count=100)
            total = get_total_count(data, term)
            print(f"'{term}' Total: {total}")
            if total < threshold:
                future = executor.submit(process_block, term, yh_all_sym, lock, 100)
                tasks.append(future)
            else:
                # Refine with a second letter if too many results
                for term2 in search_set:
                    refined_query = term + term2
                    print(f"Refining query: '{refined_query}'")
                    data = call_url(refined_query, 0, count=100)
                    total = get_total_count(data, refined_query)
                    print(f"'{refined_query}' Total: {total}")
                    if total < threshold:
                        future = executor.submit(process_block, refined_query, yh_all_sym, lock, 100)
                        tasks.append(future)
                    else:
                        # Further refine with a third character
                        for term3 in search_set:
                            refined_query2 = term + term2 + term3
                            print(f"Refining query: '{refined_query2}'")
                            data = call_url(refined_query2, 0, count=100)
                            total = get_total_count(data, refined_query2)
                            print(f"'{refined_query2}' Total: {total}")
                            if total < threshold:
                                future = executor.submit(process_block, refined_query2, yh_all_sym, lock, 100)
                                tasks.append(future)
                            else:
                                # Further refine with a fourth character
                                for term4 in search_set:
                                    refined_query3 = term + term2 + term3 + term4
                                    future = executor.submit(process_block, refined_query3, yh_all_sym, lock, 100)
                                    tasks.append(future)
        # Wait for all threads to complete
        for future in tasks:
            future.result()
    
    # Final save after processing all symbols
    update_file(yh_all_sym)
    print("Total symbols:", len(yh_all_sym))

if __name__ == '__main__':
    main()
