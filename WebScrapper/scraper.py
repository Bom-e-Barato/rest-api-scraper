from ast import arg
from posixpath import pardir
import re
import os
from sys import argv
from time import process_time
import requests
import pandas as pd
import urllib.parse
from os.path import join, dirname
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains


# Lists to store second hand names, prices and links of the products
sh_names = []
sh_prices = []
sh_links = []
sh_sites = []
sh_img=[]

# Lists to store first hand names, prices and links of the products
fh_names = []
fh_prices = []
fh_links = []


def sh_append(name, price, link, site,img):

    sh_names.append(name)
    sh_prices.append(price)
    sh_links.append(link)
    sh_sites.append(site)
    sh_img.append(img)

def sh_clear():
    sh_names.clear()
    sh_prices.clear()
    sh_links.clear()
    sh_sites.clear()
    sh_img.clear()

def data_append(data, marketplace, i):
    if marketplace == 'kk':
        data.append({
                'id': None,
                'marketplace': "kk",
                'name': fh_names[i],
                'price': fh_prices[i],
                'link': fh_links[i],
                'img': None,
                'description': None,
                'promoted': False,
                'negotiable': False,
                'id_seller': None,
                'category': None,
                'location': None
            })
    else:
        data.append({
                'id': None,
                'marketplace': marketplace,
                'name': sh_names[i],
                'price': sh_prices[i],
                'link': sh_links[i],
                'img': sh_img[i],
                'description': None,
                'promoted': False,
                'negotiable': False,
                'id_seller': None,
                'category': None,
                'location': None
            })


def olx_search(location, search_term, max_pages):
    # Olx has a max of 25 pages
    if max_pages>25:
        max_pages=25

    # Olx has a max of 25 pages
    page = requests.get(f'https://www.olx.pt/{location}/q-{search_term}/?page=1')
    soup = BeautifulSoup(page.text, 'lxml')

    n = soup.find_all('li', class_='pagination-item')
    print(int(n[-1].text))

    for i in range(int(n[-1].text)):
        page = requests.get(f'https://www.olx.pt/{location}/q-{search_term}/?page={i+1}')
        soup = BeautifulSoup(page.text, 'lxml')

        products = soup.find_all('div', class_ ='css-19ucd76')
        
        for product in products:
            try:
                # Get the data
                product_name = product.find('h6', class_='css-v3vynn-Text').text

                price_str = product.find('p', class_='css-l0108r-Text').text[:-2].replace('.', '').replace(',', '.')
                
                if price_str[-1] == 'v':
                    price_str = price_str[:-10]

                product_price = float(price_str)
                product_link = 'https://www.olx.pt/d' + product.find('a')['href']
                product_img = product.find('img')['src']
                
                # Append the data to the lists
                sh_append(name=product_name, price=product_price, link=product_link, site='olx' , img=product_img)
            except:
                continue


def cj_search(location, search_term, max_pages):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
    page_num = 1
    while True:
        page = requests.get(f'https://www.custojusto.pt/{location}/q/{search_term}?o={page_num}&sp=1&st=a', headers=headers)
        soup = BeautifulSoup(page.text, 'lxml')
        products = soup.find_all('div', class_='container_related')

        # Stop when a blank is hitted
        if not products:
            break

        for product in products:
            try:
                # Get the data
                product_name = product.find('h2', class_='title_related').find('b').text
                product_price = float(product.find('h5', class_='price_related').text.strip()[:-2].replace(' ', ''))
                product_link = product.find('a')['href']
                product_img = product.find('img')['src']

                # Append the data to the lists
                sh_append(name=product_name, price=product_price, link=product_link, site='custojusto', img=product_img)
            except:
                continue
            
        page_num = page_num + 1
        if page_num >= max_pages:
            break


def ebay_search(search_term, max_pages):
    headers = {'user-agent': 'Mozilla/5.0'}
    page_num = 1
    while True:
        page = requests.get(f'https://www.ebay.com/sch/i.html?_nkw={search_term}&_fcid=164&_sop=15&_pgn={page_num}', headers=headers)
        soup = BeautifulSoup(page.text, 'lxml')

        products = soup.find_all('li', class_='s-item')

        for product in products:
            try:             
                product_name = product.find('h3', class_='s-item__title').text
                # Retrieve the section with price and shipping information
                product_info = product.find('div', class_='s-item__details').find_all('div', class_='s-item__detail--primary')
                product_img = product.find('img')['src']
                product_base_price = 0
                cost_shipping = -1

                # Check for price and shipping cost
                for info in product_info:                
                    try:
                        product_base_price = float(info.find('span', class_='s-item__price').text[4:].replace(',', '.').replace(u'\xa0', u''))
                    except:
                        try:
                            cost_shipping = str(info.find('span', class_='s-item__shipping').text)

                            # If the text says 'grátis' then the cost is 0
                            if ('grátis' or 'não') in cost_shipping:
                                cost_shipping = 0
                            # If the text has '+' then a number is there
                            if 'EUR' in cost_shipping:
                                cost_shipping = float(cost_shipping.replace(',', '.')[5:].split()[0])
                        except:
                            # If no price or shipping are found then skip to the next div
                            continue
                
                # Remove ads that don't show the shipping price
                if cost_shipping == -1:
                    continue

                product_price = round(product_base_price + cost_shipping, 2)
                product_link = product.find('a', 's-item__link')['href']
            except:
                continue
            
            # Append the data to the lists
            sh_append(name=product_name, price=product_price, link=product_link, site='ebay', img=product_img)
            
        page_num = page_num + 1
        if page_num >= max_pages:
            break


# FacebookMarketplace search function------------------------------------------------------Probabbly illegal, too bad
def fb_search(search_term):
    """ opts = Options()
    opts.headless = True
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts) """

    dotenv_path = join(dirname(__file__),'.env')
    load_dotenv(dotenv_path)
    EMAIL = os.environ.get("EMAIL")
    PASSWORD = os.environ.get("PASSWORD")

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://www.facebook.com")
    sleep(3)

    email_input=driver.find_element_by_id("email")
    email_input.send_keys(EMAIL)

    sleep(0.5)

    pass_input=driver.find_element_by_id("pass")
    pass_input.send_keys(PASSWORD)

    sleep(0.5)

    actions = ActionChains(driver)
    actions.send_keys(Keys.ENTER)
    actions.perform()
   
    sleep(5)
    search_term=f"https://www.facebook.com/marketplace/search/?query={search_term}"
    driver.get(search_term)
    sleep(60)
    
    #content=driver.page_source
    #soup=BeautifulSoup(content,'lxml')
    #print(soup.prettify())
    #driver.close


def kk_search(search_term):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    page = requests.get(f'https://www.kuantokusta.pt/search?q={search_term}&sort=3', headers=headers)
    soup = BeautifulSoup(page.text, 'lxml')

    products = soup.find_all('div', class_='product-item-inner')
    
    for product in products:
        # Get the data
        product_name = product.find('a', class_='product-item-name')['title']
        product_price = product.find('a', class_='product-item-price').find('span').text[:-1].replace('.', '').replace(',', '.').strip()
        # Done when the price tag has text
        if 'Desde' in product_price:
            product_price = product_price[5:].strip()
        product_price = float(product_price)

        product_link = 'https://kuantokusta.pt/' + product.find('a', class_='product-item-store')['href']

        # Done when the link goes directly to the store and not to a KuantoKusta Page
        if product_link == 'https://kuantokusta.pt/#':
            encoded_link = product.find('a', class_='product-item-store')['onclick'].split(',')[2].replace('"', '').replace('\'', '').strip()
            product_link = urllib.parse.unquote(encoded_link)
        
        # Append the data to the lists
        fh_names.append(product_name)
        fh_prices.append(product_price)
        fh_links.append(product_link)

def handler(search_term, max_pages, marketplaces=['olx', 'cj', 'ebay', 'kk']):
    print("Searching for: " + search_term)
    print("Max pages: " + str(max_pages))
    print("Marketplaces: " + str(marketplaces))

    location_olx = 'ads'
    location_cj = 'portugal'

    olx_search_term = re.sub('\\s+', '-', search_term.lower().strip())      # Replace white spaces rows with '-'
    kk_search_term = re.sub('\\s+', '+', search_term.lower().strip())       # Replace white spaces rows with '+'
    cj_search_term = kk_search_term
    ebay_search_term = kk_search_term

    data = []

    if 'olx' in marketplaces:
        olx_search(location_olx, olx_search_term, max_pages)               # Populate the list with OLX data
        #sh_d = {'nomes': sh_names, 'precos': sh_prices, 'links': sh_links, 'sites': sh_sites}
        #pd.DataFrame(sh_d).sort_values('precos').to_json('sh_products.json', orient='index', indent=2, force_ascii=False)
        for i in range(len(sh_names)):
            data_append(data, 'olx', i)
        sh_clear()

    if 'cj' in marketplaces:
        cj_search(location_cj, cj_search_term, max_pages)       # Populate the list wtih CustoJusto data
        #sh_d = {'nomes': sh_names, 'precos': sh_prices, 'links': sh_links, 'sites': sh_sites}
        #pd.DataFrame(sh_d).sort_values('precos').to_json('sh_products.json', orient='index', indent=2, force_ascii=False)
        for i in range(len(sh_names)):
            data_append(data, 'cj', i)
        sh_clear()

    if 'ebay' in marketplaces:
        ebay_search(ebay_search_term, max_pages)                # Populate the list wtih eBay data
        #sh_d = {'nomes': sh_names, 'precos': sh_prices, 'links': sh_links, 'sites': sh_sites}
        #pd.DataFrame(sh_d).sort_values('precos').to_json('sh_products.json', orient='index', indent=2, force_ascii=False)
        for i in range(len(sh_names)):
            data_append(data, 'ebay', i)
        sh_clear()

    if 'kk' in marketplaces:
        kk_search(kk_search_term)                    # Populate the list wtih KuantoKusta data
        #fh_d = {'nomes': fh_names, 'precos': fh_prices, 'links': fh_links}
        #pd.DataFrame(fh_d).sort_values('precos').to_json('fh_products.json', orient='index', indent=2, force_ascii=False)
        for i in range(len(sh_names)):
            data_append(data, 'olx', i)

    print(data)
    return data


if __name__ == '__main__':
    handler(argv[2], int(argv[3]))