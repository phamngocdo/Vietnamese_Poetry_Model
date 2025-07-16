import pandas as pd
import random
import time
import re
import yaml

from tqdm import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from setup import load_driver

WEB_DRIVER_TIMEOUT = 20

with open("config/poem_type_maping.yaml", "r") as file:
    POEM_TYPE_MAPPING = yaml.safe_load(file)

def extract_vietnamese_poem_links(driver, page_idx, poem_type=16):
    """
    Extracts poem links from a specific page and poem type on thivien.net.

    Args:
        driver (webdriver): Selenium WebDriver instance.
        page_idx (int): The page index to scrape.
        poem_type (int): The type of poem to filter by.

    Returns:
        list: A list of dictionaries containing poem titles and URLs.
    """
    main_url = f"https://www.thivien.net/search-poem.php?PoemType={poem_type}&Country=2&ViewType=1&Page={page_idx}"
    driver.get(main_url)
    time.sleep(random.uniform(3, 5))

    content_tags_xpath = (
        '//*[@class="page-content container"]'
        '//div[@class="page-content-main"]'
        '//div[@class="list-item"]'
    )
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
                    "url": url
                })
            except Exception as e:
                print("Error extracting link: ", e)
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
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<i>.*?</i>", "", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<b\s*>(.*?)</b>", r"\1", html, flags=re.IGNORECASE)
    html = re.sub(r"</?p>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<.*?>", "", html)  
    return html.strip()

def extract_author(source_text):
    """
    Extracts the author's name from the source text.

    Args:
        source_text (str): The raw source text containing the author's name.

    Returns:
        str: The extracted author's name, or an empty string if not found.
    """
    match = re.match(r"^\s*([^-–—]+)", source_text.strip())
    return match.group(1).strip() if match else ""

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
    author = extract_author(poem_src)

    pattern = re.compile(r"(?:\n)?(.+?)\n{2,}", flags=re.IGNORECASE)
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
                "author": author,
                "type": POEM_TYPE_MAPPING.get(poem_type),
                "content": content,
                "url": poem_url
            })
    else:
        poems.append({
            "title": default_title,
            "author": author,
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
        poem_content_tag = WebDriverWait(driver, 20).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.poem-content"))
        )
        html_content = poem_content_tag[0].get_attribute("innerHTML")
    except Exception as e:
        print(f"Error locating poem content: {e}")
        return []

    try:
        poem_src_tag = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="small"]'))
        )
        poem_src = poem_src_tag.text
    except Exception as e:
        poem_src = ""

    return process_poem_content(html_content, poem_src, poem_url)

def scrape_poem_list(driver, num_pages=10):
    """
    Scrapes multiple pages of poems and compiles the data into a list.

    Args:
        driver (webdriver): Selenium WebDriver instance.
        num_pages (int): The number of pages to scrape.

    Returns:
        list: A list of dictionaries containing metadata and content for all poems.
    """
    datasets = []
    for page_idx in tqdm(range(1, num_pages + 1)):
        poem_type = random.randint(13, 20)
        poem_links = extract_vietnamese_poem_links(driver, page_idx, poem_type)
        for poem in poem_links:
            url = poem["url"]
            try:
                poems = scrape(driver, url)
                datasets.extend(poems)
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
    return datasets

if __name__ == "__main__":

    driver = load_driver()
    datasets = scrape_poem_list(driver, 20)
    try:
        driver.quit()
    except Exception as e:
        print(f"Error when stopping driver: {e}")
    
    df = pd.DataFrame(datasets)
    df = df[["title", "author", "type", "content", "url"]] 

    df.to_csv("data/poems_dataset.csv", index=True)
