from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

import time
import re
import pandas as pd

from tqdm import tqdm
from modules import to_pickle, scrape_elements
from collections import defaultdict


def scrape_sent(first_page, last_page, browser, url, elem_for_search, data, timeout, file_name, break_page):
    failed_pages = []
    for page in tqdm(range(first_page, last_page, 10)): 
        if page > break_page:
            break
        page_url = url + f',%22start%22:{page}%7D'
        browser.get(page_url)
        time.sleep(1)
        
        if page == first_page:
            try:
                WebDriverWait(browser, timeout).until(
                    lambda browser: browser.find_elements(By.XPATH, "//div[@class='bgs-result']"))
                time.sleep(1)

                WebDriverWait(browser, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@title='Таблицей']"))).click() 
            except Exception as e:
                print(e)
                failed_pages.append(page)

        # saving the progress every 100 pages
        if page % 100 == 0:
            to_pickle(data, file_name)

        try:
            WebDriverWait(browser, timeout).until(
                    lambda browser: browser.find_elements(By.XPATH, '//div[@data-field="case_user_doc_number"]'))
            time.sleep(2)
            table = browser.find_element_by_class_name('resultsList').find_element(By.TAG_NAME, "tbody") 
            scrape_elements(data, table, elem_for_search)
            to_pickle(data, file_name)
        except Exception as e:
            print(e, page)
            failed_pages.append(page)

    to_pickle(data, file_name)
    data.clear()
    return failed_pages