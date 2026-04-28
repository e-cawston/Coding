import requests
import os
import time

def download_beet_moth_dataset():
    taxon_key = 1849924
    limit = 1000
    folder_name = "beet_moth_dataset"
    
    # 1. Create the directory
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created folder: {folder_name}")

    print(f"Querying GBIF for Scrobipalpa ocellatella images...")

    # 2. Setup the GBIF API Search
    # We loop because GBIF returns results in pages (offset)
    downloaded_count = 0
    offset = 0
    
    while downloaded_count < limit:
        # Request a page of results
        api_url = "https://api.gbif.org/v1/occurrence/search"
        params = {
            "taxonKey": taxon_key,
            "mediaType": "StillImage",
            "limit": 100,  # Max per request
            "offset": offset
        }
        
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            print("Error connecting to GBIF API.")
            break
            
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            print("No more images found.")
            break

        for record in results:
            if downloaded_count >= limit:
                break
            
            # Find the image URL in the media list
            media = record.get("media", [])
            if not media:
                continue
                
            image_url = media[0].get("identifier")
            if not image_url:
                continue

            # 3. Attempt to download the image
            file_extension = image_url.split('.')[-1].split('?')[0] # Get clean extension
            if len(file_extension) > 4: file_extension = "jpg" # Fallback
            
            file_path = os.path.join(folder_name, f"beet_moth_{record['key']}.{file_extension}")

            try:
                img_data = requests.get(image_url, timeout=10).content
                with open(file_path, 'wb') as handler:
                    handler.write(img_data)
                downloaded_count += 1
                print(f"[{downloaded_count}/{limit}] Downloaded: {record['key']}")
            except Exception:
                print(f"Skipping broken URL: {image_url}")

        offset += 100
        time.sleep(0.1) # Be nice to the API

    print(f"\nFinished! Downloaded {downloaded_count} images to '{folder_name}'.")

if __name__ == "__main__":
    download_beet_moth_dataset()