import pandas as pd
import random
import time
import re
import yaml
import traceback

from tqdm import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from setup import load_driver

WEB_DRIVER_TIMEOUT = 40

with open("config/poem_type_maping.yaml", "r") as file:
    POEM_TYPE_MAPPING = yaml.safe_load(file)

def extract_vietnamese_poem_links(driver, page_idx, poem_type=16):
    """
    Extracts poem links from a specific page and poem type on thivien.net,
    filtering by poems with score >= 4.

    Args:
        driver (webdriver): Selenium WebDriver instance.
        page_idx (int): The page index to scrape.
        poem_type (int): The type of poem to filter by.

    Returns:
        list: A list of dictionaries containing poem titles, URLs, and scores.
    """
    main_url = f"https://www.thivien.net/search-poem.php?PoemType={poem_type}&Country=2&ViewType=1&Age[]=3&Page={page_idx}&Age%5B%5D=3"
    driver.get(main_url)
    time.sleep(random.uniform(3, 5)) 

    content_tags_xpath = '//*[@class="page-content container"]//div[@class="page-content-main"]//div[@class="list-item"]'

    try:
        content_tags = driver.find_elements(By.XPATH, content_tags_xpath)
        poem_links = []
        for tag in content_tags:
            try:
                element = tag.find_element(By.XPATH, './/h4[@class="list-item-header"]/a')
                title = element.text
                url = element.get_attribute("href")
                poem_links.append({
                    "title": title,
                    "url": url,
                
                })
            except Exception as e:
                print("Error extracting link or score: ", e)
                continue
        return poem_links
    except Exception as e:
        print("Error finding content tags: ", e)
        return []

def clean_poem_html(html):
    """
    Cleans the HTML content of a poem by removing unnecessary tags and formatting.

    Args:
        html (str): The raw HTML content of the poem.

    Returns:
        str: The cleaned text content of the poem.
    """
    html = re.sub(r"<img.*?>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<i>.*?</i>", "", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<b>(.*?)</b>(?!\s*(?:<br\s*/?>\s*){2,})" , r"\ 1", html, flags=re.IGNORECASE)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"</?p>", "", html, flags=re.IGNORECASE)
    return html.strip()


def process_poem_content(html, poem_src, poem_url, poem_type=16, default_title=""):
    """
    Processes the HTML content of a poem and extracts its metadata and content.

    Args:
        html (str): The raw HTML content of the poem.
        poem_src (str): The source text containing the author's name.
        poem_url (str): The URL of the poem.
        poem_type (int): The type of the poem.
        default_title (str): The default title to use if no title is found.

    Returns:
        list: A list of dictionaries containing poem metadata and content.
    """
    cleaned = clean_poem_html(html)

    pattern = re.compile(r"<b>(.*?)</b>\s*\n{2,}", flags=re.IGNORECASE)
    matches = list(pattern.finditer(cleaned))

    poems = []

    if matches:
        for i, match in enumerate(matches):
            title = match.group(1).strip()
            start = match.end()
            end = matches[i+1].start() if i + 1 < len(matches) else len(cleaned)
            content = cleaned[start:end].strip()
            poems.append({
                "title": title,
                "type": POEM_TYPE_MAPPING.get(poem_type),
                "content": content,
                "url": poem_url
            })
    else:
        poems.append({
            "title": default_title,
            "type": POEM_TYPE_MAPPING.get(poem_type),
            "content": cleaned,
            "url": poem_url
        })

    return poems

def scrape(driver, poem_url):
    """
    Scrapes the content of a single poem from its URL.

    Args:
        driver (webdriver): Selenium WebDriver instance.
        poem_url (str): The URL of the poem to scrape.

    Returns:
        list: A list of dictionaries containing poem metadata and content.
    """
    driver.get(url=poem_url)
    time.sleep(random.uniform(3, 5)) 

    try:
        poem_content_tag = WebDriverWait(driver, WEB_DRIVER_TIMEOUT).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.poem-content"))
        )
        html_content = poem_content_tag[0].get_attribute("innerHTML")
    except Exception as e:
        print(f"Error locating poem content: {e}")
        traceback.print_exc()
        return []

    try:
        poem_src_tag = WebDriverWait(driver, WEB_DRIVER_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="small"]'))
        )
        poem_src = poem_src_tag.text
    except Exception as e:
        poem_src = ""

    return process_poem_content(html_content, poem_src, poem_url)

def scrape_poem_list_with_type(driver, num_pages=10, poem_type=16):
    """
    Scrapes a list of Vietnamese poems from thivien.net across multiple pages and types.

    Args:
        driver (webdriver): Selenium WebDriver instance used for web scraping.
        num_pages (int): Number of pages to scrape for each poem type.

    Returns:
        list: A list of dictionaries, each containing metadata and content of a scraped poem.
              The metadata includes title, author, type, content, and URL.
    """

    datasets = []
    for page_idx in tqdm(range(1, num_pages + 1), desc=f"Type {poem_type}"):
        poem_links = extract_vietnamese_poem_links(driver, page_idx, poem_type)
        for poem in poem_links:
            url = poem["url"]
            try:
                poems = scrape(driver, url)
                for poem_dict in poems:
                    poem_dict["type"] = POEM_TYPE_MAPPING.get(poem_type)
                datasets.extend(poems)
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
    return datasets

def scrape_poem_list(driver, num_pages=10):
    """
    Scrapes a list of Vietnamese poems from thivien.net across multiple pages and types.

    Args:
        driver (webdriver): Selenium WebDriver instance used for web scraping.
        num_pages (int): Number of pages to scrape for each poem type.

    Returns:
        list: A list of dictionaries, each containing metadata and content of a scraped poem.
              The metadata includes title, author, type, content, and URL.
    """
    datasets = []
    for poem_type in POEM_TYPE_MAPPING.keys():
        datasets.extend(scrape_poem_list_with_type(driver, num_pages, poem_type))
    return datasets

if __name__ == "__main__":
    driver = load_driver()
    datasets = scrape_poem_list_with_type(driver, 10, 16) # Adjust the type of poem as needed or use scrape_poem_list for all types
    try:
        driver.quit()
    except Exception as e:
        print(f"Error when stopping driver: {e}")
    
    if not datasets:
        print("No data was scraped.")
    else:
        for poem in datasets:
            poem.setdefault("title", "Unknown Title")
            poem.setdefault("type", "Unknown Type")
            poem.setdefault("content", "No Content")
            poem.setdefault("url", "No URL")
        
        df = pd.DataFrame(datasets)
        print(df.columns)  
        df = df[["title", "author", "type", "content", "url"]] 
        df.to_csv("data/poems_dataset.csv", index=True)
