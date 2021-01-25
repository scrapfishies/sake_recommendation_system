'''
Functions to scrape TrueSake.com!
'''

# Imports
import pandas as pd
import re
from random import randint
from time import sleep
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests


def find_product_list_urls(start_url):
    '''
    Finds all product listing urls based on total results available
    -------------
    Inputs: product listing url
    Outputs: list of listing urls for all results
    '''
    response = requests.get(start_url)
    page = response.text
    soup = BeautifulSoup(page, 'html.parser')

    last_page = soup.find_all('a', class_='pagination--item')[-2].text
    regex = re.compile(r'[\n\s+]')
    last_page = int(regex.sub("", last_page))

    pages = range(1, last_page+1)

    url_list = []

    for page in pages:
        url = url_prefix = f'https://www.truesake.com/collections/all?page={page}&grid_list=grid-view'
        url_list.append(url)

    return url_list


def get_product_urls(url_list):
    '''
    Finds all individual product urls
    -------------
    Inputs: a list of product listings urls
    Outputs: list of listing urls for all individual products
    '''
    product_links = []

    for url in url_list:
        response = requests.get(url)
        page = response.text
        soup = BeautifulSoup(page, 'html.parser')

        # Find product linkk tags:
        produt_link_a_tags = soup.find_all('a', 'productitem--image-link')

        # product links
        links = ['https://www.truesake.com'+l['href']
                 for l in produt_link_a_tags]
        for link in links:
            product_links.append(link)

    print(len(product_links), 'product urls scraped')
    return product_links


def find_product_keywords(full_description_text):
    '''
    Helper function for `get_product_info` scraper
    Finds up to 4 main keywords to describe the sake
    -------------
    Inputs: description text
    Outputs: up to 4 keywords to describe the sake
    '''
    keywords = ["WORD: ", "WINE: ", "BEER: ", "FOODS: "]
    available_kws = [
        kw for kw in keywords if full_description_text.find(kw) > 0]

    kw_results_dict = {}
    kw_results = []

    for i in range(len(available_kws)):

        if i < len(available_kws)-1:
            kw = re.search(
                f'{available_kws[i]}(.*){available_kws[i+1]}', full_description_text).group(1)
        else:
            kw = re.search(
                f'{available_kws[i]}(.*)', full_description_text).group(1)

        kw_results_dict[available_kws[i]] = kw

    for word in keywords:
        try:
            result = kw_results_dict[word]
        except:
            result = 'Missing'
        kw_results.append(result)

    return kw_results


def get_product_info(prod_url):
    '''
    Scrapes product page and compiles results into a list
    -------------
    Inputs: url for product page
    Outputs: all availble information about the sake in a list
    '''
    # Beautiful Soup Setup
    response = requests.get(prod_url)
    page = response.text
    soup = BeautifulSoup(page, 'html.parser')

    # Find product description part of html
    product_description_html = soup.find('div', class_='product-main')

    # Product Name
    try:
        name = product_description_html.find('h1').text
        name = re.sub(r'[\n]', "", name).strip()

    except Exception as e:
        name = 'Missing'

    # Sake Type
    try:
        sake_type = product_description_html.find(
            'div', class_='product-metafields--sake-type').text
        sake_type = re.sub(r'[\n]', '', sake_type).strip()

    except Exception as e:
        sake_type = 'Missing'

    # Product Price
    try:
        price = product_description_html.find('div', class_='price--main').text
        price = re.sub(r'[\n]', '', price).strip()[1:]

    except Exception as e:
        price = 'Missing'

    # Product description section
    try:
        full_description = product_description_html.find(
            'div', class_='product-description rte').text
        full_description = re.sub(r'[\n]', '', full_description)

        # 4 main keywords
        results = find_product_keywords(full_description)

        keyword_word = results[0]      # Word
        keyword_wine = results[1]      # Wine
        keyword_beer = results[2]      # Beer
        keyword_foods = results[3]     # Foods

    except Exception as e:
        full_description = 'Missing'
        keyword_word = 'Missing'
        keyword_wine = 'Missing'
        keyword_beer = 'Missing'
        keyword_foods = 'Missing'

    # Prefecture
    try:
        details = product_description_html.find_all(
            'div', class_='product-metafields--result')
        prefecture = details[0].text
        prefecture = re.sub(r'[\n]', '', prefecture).strip()

    except Exception as e:
        prefecture = 'Missing'

    # SMV
    try:
        # Other Sake Descriptions
        details = product_description_html.find_all(
            'div', class_='product-metafields--result')
        smv = details[1].text
        smv = re.sub(r'[\n]', '', smv).strip()

    except Exception as e:
        smv = 'Missing'

    # Acidity
    try:
        # Other Sake Descriptions
        details = product_description_html.find_all(
            'div', class_='product-metafields--result')
        acidity = details[2].text
        acidity = float(re.sub(r'[\n]', '', acidity).strip())

    except Exception as e:
        acidity = 'Missing'

    # Compile results list
    results_list = [prod_url,
                    name,
                    sake_type,
                    price,
                    prefecture,
                    smv,
                    acidity,
                    keyword_word,
                    keyword_wine,
                    keyword_beer,
                    keyword_foods,
                    full_description]

    return results_list


def scrape_truesake(start_url):
    '''
    Final function to scrape all results!
    -------------
    Inputs: a start url -- the first page of results listings
    Outputs: a pandas DataFrame containing all available products
    '''

    print("Starting scrape...")

    products = []
    count = 1

    # Get all product listings pages
    product_listings_url_list = find_product_list_urls(start_url)
    print("Product listings url list compiled!")

    # get all individual product urls
    individual_product_urls = get_product_urls(product_listings_url_list)
    print("Individual product url list compiled!")

    print("\nStarting product url scrape...")
    for url in tqdm(individual_product_urls):

        # Set sleep interval to slow down requests
        sleep(randint(1, 2))

        # Scrape product url page
        product_details = get_product_info(url)
        products.append(product_details)

        count += 1

    # Compiling results into a pandas DF
    columns = ['url', 'name', 'type', 'price', 'prefecture', 'smv', 'acidity',
               'kw_word', 'kw_wines', 'kw_beer', 'kw_foods', 'description']

    df = pd.DataFrame(products, columns=columns)

    print(f"{count} products scraped!")
    return df
