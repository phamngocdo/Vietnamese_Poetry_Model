import pandas as pd
import random
import time
import re

from tqdm import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from setup import load_driver

WEB_DRIVER_TIMEOUT = 20

def extract_vietnamese_poem_links(driver, page_idx, poem_type=16):
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
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<i>.*?</i>", "", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<b\s*>(.*?)</b>", r"\1", html, flags=re.IGNORECASE)
    html = re.sub(r"</?p>", "", html, flags=re.IGNORECASE)
    html = re.sub(r"<.*?>", "", html)  
    return html.strip()

def extract_author(source_text):
    match = re.match(r"^\s*([^-–—]+)", source_text.strip())
    return match.group(1).strip() if match else ""

def process_poem_content(html, poem_src, poem_url, default_title=""):
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
                "content": content,
                "url": poem_url
            })
    else:
        poems.append({
            "title": default_title,
            "author": author,
            "content": cleaned,
            "url": poem_url
        })

    return poems

def scrape(driver, poem_url):
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
    datasets = []
    for page_idx in tqdm(range(1, num_pages + 1)):
        poem_links = extract_vietnamese_poem_links(driver, page_idx, random.randint(13,20))
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
    datasets = scrape_poem_list(driver, 10)
    try:
        driver.quit()
    except Exception as e:
        print(f"Error when stop driver: {e}")
    
    df = pd.DataFrame(datasets)
    df = df[["title", "author", "content", "url"]] 

    df.to_csv("data/poems_dataset.csv", index=True)
