import pandas as pd
from googlesearch import search
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urljoin
from time import sleep
import re
from urllib.parse import urlparse, urlunparse
from retry import retry


def create_school_name(row):
    # Concatenate Fullname, City, State, Country, and add 'Logo' at the end
    name = f"{row['FullName']} {row['City']} {row['State']} {row['Country']}"
    name = name.replace('/', '').replace('\\', '')  # Remove both slashes
    return name


def download_images(query, num_images=4, download_path='images'):
    school_name = query
    # Create download directory if not exists
    os.makedirs(download_path, exist_ok=True)

    # Check if a file with the school name already exists in the download path
    if any(query.lower() in filename.lower() for filename in os.listdir(download_path)):
        print(f"Skipping download for {query}: File already exists")
        return

    # Set logo_found flag inside the function to reset it for each school name
    if 'Miltown Malbay Miltown Malbay Clare' in query:
        query = query.replace('Miltown Malbay Miltown Malbay Clare', '')
    search_results = search(query + 'Logo', num_results=num_images, lang='en')

    # Download images
    for i, result in enumerate(search_results):
        try:
            if i >= num_images: # or logo_found:
                break
            print(result)
            # if 'wikipedia' in result:
            #     continue
            # Fetch HTML content
            @retry(ConnectionError, tries=6, delay=2, backoff=2)
            def get_with_retry(url):
                return requests.get(url, timeout=1090)

            response = get_with_retry(result)
            soup = BeautifulSoup(response.text, 'html.parser')

            img_tags = soup.find_all('img')

            # Download images
            for j, img_tag in enumerate(img_tags):
                # if logo_found:
                #     break

                # img_url = img_tag.get('srcset')
                # if not img_url:
                #     img_url = img_tag.get('src')
                img_url = img_tag.get('src')
                # Skip if the image URL is not present
                if not img_url:
                    continue
                logo_not_check = ['fb', 'twitter', 'insta', 'office', 'youtube', 'way2pay', 'Vs', 'Easy Payments',
                                  'Footer', 'tracker', 'icon', 'vsware', 'facebook', 'iclass', 'https://www.schooldays.ie/',
                                  'irelandstats', 'google', 'ceist', 'twimg', 'erros', 'mapbox']
                if any(check.lower() in img_url.lower() for check in logo_not_check):
                    continue
                # logo_check = ['logo', 'Logo', 'profile_image']
                # if not any(check in img_url for check in logo_check):
                #     continue

                # Join relative URLs with the base URL
                img_url = urljoin(result, img_url)
                # if ',' in img_url:
                #     urls = img_url.split(',')
                #
                #     # Extract full-size URLs for each URL
                #     full_size_urls = []
                #     for url in urls:
                #         # Split the URL into parts
                #         parts = url.strip().split(' ')
                #         img_url = parts[0]

                # Download the image
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    print(img_url)
                    img_filename = f"{download_path}/{school_name}_logo_{i+j+1}.jpg"
                    with open(img_filename, 'wb') as f:
                        f.write(img_response.content)
                    print(f"Downloaded {img_filename}")
                    logo_found = True  # Set the flag to True if at least one logo is found
        except Exception as e:
            print(e)


if __name__ == "__main__":
    found_logos = {}
    not_found = []
    # Read XLSX file and create a DataFrame
    xlsx_file = 'School_list.xlsx'  # Replace with your XLSX file path
    df = pd.read_excel(xlsx_file)
    not_found_logos = []
    # Create a school name list by concatenating Fullname, City, State, Country, and adding 'Logo'
    all_school_names = [create_school_name(row).replace('/', '').replace('\'', '').replace(':', '').replace("'", '').replace(',', '') for _, row in
                        df.iterrows()]

    # Folder path containing the logos
    folder_path = 'final_logos'
    for index, school_name in enumerate(all_school_names):
        # Check if any logo file in the folder contains or starts with the school name
        matching_logos = [filename.replace(',', '').replace(':', '') for filename in os.listdir(folder_path) if school_name.lower() in filename.lower().replace(':', '').replace(',', '') or filename.lower().replace(',', '').replace(':', '').startswith(school_name.lower())]

        if matching_logos:
            print(f" {index}:  Found logo for {school_name}: {matching_logos}")
        else:
            print(f" {index}:  Logo not found for {school_name}")
            not_found_logos.append(school_name)

    # Print or use the results as needed
    print("\nSchool Names without Logos:")
    for index, school_name in enumerate(not_found_logos, start=1):
        print(f"  {index}. {school_name}")
        download_images(school_name)
    print('Done')
