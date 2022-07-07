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
from collections import defaultdict

from modules import to_pickle, scrape_elements
from scrape_sentences import scrape_sent

if __name__ == '__main__':
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--no-sandbox')
    failed_pages = []

    elem_for_search = [
        "case_user_doc_number",
        "adm_case_user_name",
        "case_common_parts_law_article",
        "case_user_entry_date",
        "case_doc_subject_rf",
        "case_user_doc_court",
        "case_user_doc_result",
        "case_user_doc_result_date", 
        'link'
    ]
    timeout = 100

    for p in range(0, 86330, 1000):
        first_page = p
        last_page = p + 1010
        file_name = 'data_19_3_' + str(last_page)
        data = defaultdict(list,{ k:[] for k in elem_for_search })
        url = 'https://bsr.sudrf.ru/bigs/portal.html#%7B%22type%22:%22MULTIQUERY%22,%22multiqueryRequest%22:%7B%22queryRequests%22:%5B%7B%22type%22:%22Q%22,%22request%22:%22%7B%5C%22mode%5C%22:%5C%22EXTENDED%5C%22,%5C%22typeRequests%5C%22:%5B%7B%5C%22fieldRequests%5C%22:%5B%7B%5C%22name%5C%22:%5C%22case_user_doc_entry_date%5C%22,%5C%22operator%5C%22:%5C%22B%5C%22,%5C%22query%5C%22:%5C%222022-01-01T00:00:00%5C%22,%5C%22sQuery%5C%22:%5C%222022-07-01T00:00:00%5C%22,%5C%22fieldName%5C%22:%5C%22case_user_doc_entry_date%5C%22%7D,%7B%5C%22name%5C%22:%5C%22case_doc_instance%5C%22,%5C%22operator%5C%22:%5C%22EX%5C%22,%5C%22query%5C%22:%5C%22%D0%9F%D0%B5%D1%80%D0%B2%D0%B0%D1%8F%20%D0%B8%D0%BD%D1%81%D1%82%D0%B0%D0%BD%D1%86%D0%B8%D1%8F%5C%22,%5C%22sQuery%5C%22:null%7D,%7B%5C%22name%5C%22:%5C%22case_common_parts_law_article%5C%22,%5C%22operator%5C%22:%5C%22EX%5C%22,%5C%22query%5C%22:%5C%2219.3%5C%22,%5C%22sQuery%5C%22:null%7D,%7B%5C%22name%5C%22:%5C%22case_common_parts_law_article%5C%22,%5C%22operator%5C%22:%5C%22EX%5C%22,%5C%22query%5C%22:%5C%22%D1%81%D1%82.%2019.3%5C%22,%5C%22sQuery%5C%22:null%7D%5D,%5C%22mode%5C%22:%5C%22AND%5C%22,%5C%22name%5C%22:%5C%22common%5C%22,%5C%22typesMode%5C%22:%5C%22AND%5C%22%7D%5D%7D%22,%22operator%22:%22AND%22,%22queryRequestRole%22:%22CATEGORIES%22%7D,%7B%22type%22:%22SQ%22,%22queryId%22:%221f074cdd-f56a-4089-b901-df7a05b3a5c8%22,%22operator%22:%22AND%22%7D%5D%7D,%22sorts%22:%5B%7B%22field%22:%22score%22,%22order%22:%22desc%22%7D%5D,%22simpleSearchFieldsBundle%22:null,%22groups%22:%5B%5D,%22noOrpho%22:false'
        browser = webdriver.Chrome(ChromeDriverManager().install(), ) # options=chrome_options
        failed_pages.append(scrape_sent(first_page, last_page, browser, url, elem_for_search, data, timeout, file_name))
        browser.close()
        to_pickle(failed_pages, 'failed_pages_19_3')