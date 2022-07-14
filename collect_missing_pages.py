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

def pickle_to_list(path):
	with open(path, "rb") as fp:
		temp_list = pickle.load(fp)
	temp_list = [i for i in temp_list if i !=[]] # remove empty lists
	temp_list = [c for i in temp_list for c in i] # unpack list if lists
	return temp_list

def collect_missing_pages(missing_pages:list, elem_for_search, timeout, file_name:str, url):
	data = defaultdict(list,{ k:[] for k in elem_for_search })
	browser = webdriver.Chrome(ChromeDriverManager().install(), )
	first_page = True
	for page in tqdm(missing_pages): 
		page_url = url + f',%22start%22:{page}%7D'
		browser.get(page_url)
		time.sleep(1)
		if first_page:
			try:
				WebDriverWait(browser, timeout).until(
					lambda browser: browser.find_elements(By.XPATH, "//div[@class='bgs-result']"))
				time.sleep(1)

				WebDriverWait(browser, timeout).until(
					EC.element_to_be_clickable((By.XPATH, "//a[@title='Таблицей']"))).click() 
			except Exception as e:
				print(e, 'on a page', page)
			first_page = False

		try:
			WebDriverWait(browser, timeout).until(
				lambda browser: browser.find_elements(By.XPATH, '//div[@data-field="case_user_doc_number"]'))
			time.sleep(2)
			table = browser.find_element_by_class_name('resultsList').find_element(By.TAG_NAME, "tbody") 
			scrape_elements(data, table, elem_for_search)
			to_pickle(data, file_name)
		except Exception as e:
			print(e, 'on a page', page)
		to_pickle(data, file_name)
	data.clear()


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
missing_pages = [2340, 2840]
file_name = 'missing_data_20_2_2022_'
url = 'https://bsr.sudrf.ru/bigs/portal.html#%7B%22type%22:%22MULTIQUERY%22,%22multiqueryRequest%22:%7B%22queryRequests%22:%5B%7B%22type%22:%22Q%22,%22request%22:%22%7B%5C%22mode%5C%22:%5C%22EXTENDED%5C%22,%5C%22typeRequests%5C%22:%5B%7B%5C%22fieldRequests%5C%22:%5B%7B%5C%22name%5C%22:%5C%22case_user_doc_entry_date%5C%22,%5C%22operator%5C%22:%5C%22B%5C%22,%5C%22query%5C%22:%5C%222022-01-01T00:00:00%5C%22,%5C%22fieldName%5C%22:%5C%22case_user_doc_entry_date%5C%22%7D,%7B%5C%22name%5C%22:%5C%22case_common_parts_law_article%5C%22,%5C%22operator%5C%22:%5C%22EX%5C%22,%5C%22query%5C%22:%5C%22%D1%81%D1%82.%2020.2%5C%22,%5C%22sQuery%5C%22:null%7D%5D,%5C%22mode%5C%22:%5C%22AND%5C%22,%5C%22name%5C%22:%5C%22common%5C%22,%5C%22typesMode%5C%22:%5C%22AND%5C%22%7D%5D%7D%22,%22operator%22:%22AND%22,%22queryRequestRole%22:%22CATEGORIES%22%7D,%7B%22type%22:%22SQ%22,%22queryId%22:%221f074cdd-f56a-4089-b901-df7a05b3a5c8%22,%22operator%22:%22AND%22%7D%5D%7D,%22sorts%22:%5B%7B%22field%22:%22score%22,%22order%22:%22desc%22%7D%5D,%22simpleSearchFieldsBundle%22:null,%22groups%22:%5B%22%D0%94%D0%B5%D0%BB%D0%B0%20%D0%BE%D0%B1%20%D0%90%D0%9F%22%5D,%22noOrpho%22:false'


collect_missing_pages(missing_pages, elem_for_search, timeout, file_name, url)