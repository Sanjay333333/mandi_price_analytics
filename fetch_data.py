import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_and_save():
    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    api_key = os.getenv("API_KEY")

    params = {
        "api-key": api_key,
        "format": "json",
        "limit": 1000,
        "filters[state.keyword]": "Tamil Nadu"
    }

    headers = {
        "User-Agent": "AgritechDataPipeline/1.0"
    }

    print("Fetching live market data from API...")
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        records = data.get('records', [])
        
        if records:
            # Save ONLY the records array
            with open("live_data.json", "w") as f:
                json.dump(records, f)
            print(f"Success! Saved {len(records)} rows to live_data.json.")
        else:
            print("API call successful, but no records were returned.")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    fetch_and_save()