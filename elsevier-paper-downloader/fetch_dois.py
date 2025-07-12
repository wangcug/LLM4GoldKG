import requests
import json
import os
import time
import math
from datetime import datetime

API_KEY = "your own API key"  # replace with your Elsevier API key
SEARCH_QUERY = "gold deposit"  # search keywords
MAX_RESULTS = 500  # maximum retrievable number of ducuments
RESULTS_PER_PAGE = 25
API_BASE_URL = "https://api.elsevier.com/content/search/scopus"
OUTPUT_FILENAME = "doi_list.json"


def fetch_doi_list():
    dois = []
    total_results = 0
    retrieved = 0
    start = 0

    print(f"retrieval of ducument DOI list is initiated，search: '{SEARCH_QUERY}'")

    try:
        while retrieved < MAX_RESULTS:
            params = {
                "query": SEARCH_QUERY,
                "apiKey": API_KEY,
                "start": start,
                "count": RESULTS_PER_PAGE
            }

            response = requests.get(API_BASE_URL, params=params,
                                    headers={"Accept": "application/json"})

            if response.status_code != 200:
                print(f"API request failed: HTTP {response.status_code}")
                print(f"response: {response.text[:200]}")
                break

            data = response.json()

            if start == 0:
                total_results = min(
                    int(data['search-results']['opensearch:totalResults']),
                    MAX_RESULTS
                )
                print(f" {total_results} relevant ducuments were retrieved")

            entries = data['search-results'].get('entry', [])
            if not entries:
                print("no more results")
                break

            for item in entries:
                if 'prism:doi' in item:
                    dois.append(item['prism:doi'])
                    retrieved += 1
                if retrieved >= MAX_RESULTS:
                    break

            print(f"DOI for {retrieved}/{total_results} documents have been obtained")

            if retrieved >= total_results:
                break

            start += RESULTS_PER_PAGE

            time.sleep(0.5)

    except requests.exceptions.RequestException as e:
        print(f"network request error: {str(e)}")
    except KeyError as e:
        print(f"response data parsing error: {str(e)}")
        print("API response content:", response.text[:500])
    except json.JSONDecodeError:
        print("API response is not valid JSON")
        print("response content:", response.text[:500])
    except Exception as e:
        print(f"unknown error: {str(e)}")

    return dois

def save_doi_list(dois):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, OUTPUT_FILENAME)

    data = {
        "query": SEARCH_QUERY,
        "timestamp": datetime.now().isoformat(),
        "count": len(dois),
        "dois": dois
    }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"succsessfully saved {len(dois)} DOI to the {output_path}")
    return output_path

def main():
    doi_list = fetch_doi_list()

    if not doi_list:
        print("No doi retrieved. Please check your query parameters or API key")
        return

    save_doi_list(doi_list)

if __name__ == "__main__":
    main()