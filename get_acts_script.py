from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
import time
import re
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, filemode='a', filename='sud_parser_log.log', format='%(asctime)s %(levelname)s:%(message)s')

def attr_to_df(document_type, entry_date, subject_rf, court, instance, category_article, result, case, links, extr_mat, annotation, name):
    logging.info(f'__{extr_mat[0]}__ записываю данные в датафрейм')
    df = pd.DataFrame(columns=[
        'Экстремистский_материал',
        'Тип_документа',
        'Название_дела',
        'Дата',
        'Субъект',
        'Название_суда',
        'Инстанция',
        'Статья',
        'Результат',
        'Краткая_аннотация',
        'Ссылка'
    ])
    df['Тип_документа'] = document_type
    df['Дата'] = entry_date
    df['Субъект'] = subject_rf
    df['Название_суда'] = court
    df['Инстанция'] = instance
    df['Статья'] = category_article
    df['Результат'] = result
    df['Название_дела'] = case
    df['Ссылка'] = links
    df['Экстремистский_материал'] = extr_mat
    df['Краткая_аннотация'] = annotation
    
    print(f'Создан датафрейм размером: {df.shape}')
    logging.info(f'__{extr_mat[0]}__ создан датафрейм размером: {df.shape}')
    path = r'C:\Users\kiril\OneDrive\Projects\sud_scraper_v2\materials_data'
    output_file = os.path.join(path, name)
    df.to_csv(output_file, encoding='utf-8', index=False)

def get_acts(material_name):
    logging.info("Название материала: %s", material_name)
    timeout = 60
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument("start-maximized")
    # browser = webdriver.Chrome('chromedriver', options=chrome_options)

    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    # browser = webdriver.Chrome('chromedriver')
    # создаем списки, в которые будут добавляться данные по актам
    doc_type, entry_date, subject, court, instance, article, result, case, link, material, anno  = [[] for i in range(11)]
    
    # создаём шаблон страницы, с которой будут собираться данные по актам
    start_page = 0
    part_url_first = 'https://bsr.sudrf.ru/bigs/portal.html#{"type":"MULTIQUERY","multiqueryRequest":{"queryRequests":[{"type":"Q","queryRequestRole":"SIMPLE","request":"{\\"query\\":'
    part_url_key = f'\\"{material_name}\\",'
    part_url_close = '\\"type\\":\\"EXACT\\",\\"mode\\":\\"SIMPLE\\"}","operator":"AND"},{"type":"Q","request":"{\\"mode\\":\\"EXTENDED\\",\\"typeRequests\\":[{\\"fieldRequests\\":[{\\"name\\":\\"case_document_category_article_cat\\",\\"operator\\":\\"SEW\\",\\"query\\":\\"20.29\\",\\"fieldName\\":\\"case_document_category_article_cat\\"}],\\"mode\\":\\"AND\\",\\"name\\":\\"common\\",\\"typesMode\\":\\"AND\\"}]}","operator":"AND","queryRequestRole":"CATEGORIES"}]},"sorts":[{"field":"score","order":"desc"}],"simpleSearchFieldsBundle":"default","noOrpho":false'
    part_url_page = f',"start":{start_page}' + '}'
    start_url = part_url_first + part_url_key + part_url_close + part_url_page
    
    # Загружаем страницу
    browser.get(start_url)
    # Проверяем загрузилась ли страница
    try:
        WebDriverWait(browser, timeout).until(
            lambda browser: browser.find_elements(By.XPATH, "//div[@class='bgs-result']") or browser.find_elements(By.XPATH, "//div[contains(text(), 'Ничего не найдено')]"))
        print('page loaded')
        empty_req = browser.find_elements(By.XPATH, "//div[contains(text(), 'Ничего не найдено')]")
        logging.info(f'__{material_name}__ страница загружена')
        # Проверяем не пустая ли страница
        if empty_req != []:
            print('Нет актов по этому запросу')
            logging.info(f'__{material_name}__ пустой запрос')
            browser.close()
            return(None,)*11
    
    except:
        logging.exception(f'__{material_name}__ страница не загрузилась')
        browser.close()
        return(None,)*11

    # Собираем акты  
    try:
        # Находим номер последней страницы
        pages = browser.find_elements_by_tag_name('td.pageNumTD')
        
        # Если в запросе только одна страница
        if pages == []:
            headers = browser.find_elements_by_tag_name('a.resultHeader')
            annotations = browser.find_elements_by_tag_name('div.resultText')
            for i in headers:
                link.append(i.get_attribute('href'))
                case.append(i.text)
            for i in annotations:
                anno.append(i.text)
            WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[1]/div[2]/div/div/div[2]/div[3]/div[1]/span[2]/a[2]'))).click()
            table = browser.find_element_by_class_name('resultsList').find_elements_by_tag_name('tbody')
            for row in table:
                case_user_document_type = [doc_type.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_document_type"]')]
                case_user_doc_entry_date = [entry_date.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_doc_entry_date"]') or row.find_elements_by_xpath('//div[@data-field="case_user_entry_date"]')]
                case_doc_subject_rf = [subject.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_doc_subject_rf"]')]
                case_user_doc_court = [court.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_doc_court"]')]
                case_doc_instance = [instance.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_doc_instance"]')]
                case_document_category_article = [article.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_document_category_article"]')]
                case_user_doc_result = [result.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_doc_result"]')]

            material = [material_name for i in range(len(doc_type))]
            
            browser.close()
            return doc_type, entry_date, subject, court, instance, article, result, case, link, material, anno
        
        # Находим номер последней страницы
        last_page = int(pages[-1].text)
        
        # Если в запросе больше 50 страниц
        if last_page > 50:
            logging.warning(f'__{material_name}__ больше 50 страниц')
            browser.close()
            return(None,)*11
        
        logging.info(f'__{material_name}__ найдено {last_page} страниц')
        last_page = last_page * 10
        
        # Если в запросе меньше 50 страниц
        # Начинаем листать страницы
        for page in range(10, last_page, 10):
            # Ищем ссылки и заголовки дел
            headers = browser.find_elements_by_tag_name('a.resultHeader')
            annotations = browser.find_elements_by_tag_name('div.resultText')
            for i in headers:
                link.append(i.get_attribute('href'))
                case.append(i.text)
            for i in annotations:
                anno.append(i.text)

            # Переключаем страницу на табличный вид
            WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[1]/div[2]/div/div/div[2]/div[3]/div[1]/span[2]/a[2]'))).click()
            time.sleep(1)

            # Ищем таблицу с аттрибутами актов 
            table = browser.find_element_by_class_name('resultsList').find_elements_by_tag_name('tbody')
            for row in table:
                case_user_document_type = [doc_type.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_document_type"]')]
                case_user_doc_entry_date = [entry_date.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_doc_entry_date"]') or row.find_elements_by_xpath('//div[@data-field="case_user_entry_date"]')]
                case_doc_subject_rf = [subject.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_doc_subject_rf"]')]
                case_user_doc_court = [court.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_doc_court"]')]
                case_doc_instance = [instance.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_doc_instance"]')]
                case_document_category_article = [article.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_document_category_article"]')]
                case_user_doc_result = [result.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_doc_result"]')]

            logging.info(f'__{material_name}__ на странице {page} собрано ссылок({len(headers)}), заголовков({len(headers)}), аннотаций({len(annotations)}), аттрибутов {len(case_user_document_type)}')
            # Переключаем страницу на списочный вид
            WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[1]/div[2]/div/div/div[2]/div[3]/div[1]/span[2]/a[1]'))).click()
            time.sleep(1)
            
            # Формируем url следующей страницы
            part_url_key = f'\\"{material_name}\\",'
            part_url_page = f',"start":{page}' + '}'
            url = part_url_first + part_url_key + part_url_close + part_url_page
            browser.get(url)
            WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, "//*[@class='resultHeader openCardLink']")))
            time.sleep(1)
            
        # Собираем акты на последней странице вне цикла
        headers = browser.find_elements_by_tag_name('a.resultHeader')
        annotations = browser.find_elements_by_tag_name('div.resultText')
        for i in headers:
            link.append(i.get_attribute('href'))
            case.append(i.text)
        for i in annotations:
            anno.append(i.text)
        logging.info(f'__{material_name}__ на последней странице собрано ссылок({len(headers)}), заголовков({len(headers)}), аннотаций({len(annotations)}), аттрибутов {len(case_user_document_type)}')

        # Переключаем страницу на табличный вид
        WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[1]/div[2]/div/div/div[2]/div[3]/div[1]/span[2]/a[2]'))).click()
        time.sleep(1)

        # Ищем таблицу с аттрибутами актов 
        table = browser.find_element_by_class_name('resultsList').find_elements_by_tag_name('tbody')
        for row in table:
            case_user_document_type = [doc_type.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_document_type"]')]
            case_user_doc_entry_date = [entry_date.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_doc_entry_date"]') or row.find_elements_by_xpath('//div[@data-field="case_user_entry_date"]')]
            case_doc_subject_rf = [subject.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_doc_subject_rf"]')]
            case_user_doc_court = [court.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_doc_court"]')]
            case_doc_instance = [instance.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_doc_instance"]')]
            case_document_category_article = [article.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_document_category_article"]')]
            case_user_doc_result = [result.append(i.text) for i in row.find_elements_by_xpath('//div[@data-field="case_user_doc_result"]')]

        logging.info(f'__{material_name}__ собрано всего: doc_type: {len(doc_type)}, entry_date: {len(entry_date)},subject: {len(subject)}, court: {len(court)}, instance: {len(instance)}, article: {len(article)}, result: {len(result)}, case: {len(case)}, link: {len(link)}, material: {len(material)}, anno: {len(anno)}')

    except TimeoutException:
        logging.exception(f'__{material_name}__ страница не загрузилась. Ошибка TimeoutException')
        browser.close()
        return(None,)*11
    except IndexError:
        logging.exception(f'__{material_name}__ Ошибка IndexError')
        browser.close()
        return(None,)*11
    except ElementClickInterceptedException:
        logging.exception(f'__{material_name}__ Ошибка ElementClickInterceptedException')
        browser.close()
        return(None,)*11
    except StaleElementReferenceException:
        logging.exception(f'__{material_name} Ошибка StaleElementReferenceException')
        browser.close()
        return(None,)*11
        
    material = [material_name for i in range(len(doc_type))]
    browser.close()
    return doc_type, entry_date, subject, court, instance, article, result, case, link, material, anno



# открываю список экстремистских материалов
# with open('material_without_duplicates.txt') as f:
#     extr_material_list = f.read().splitlines()

extr_material_list = ['припомним жуликам и ворам', 'музыка белых']

# Запуск кода
start = time.time()
if __name__ == "__main__":
    counter = 0
    for mater in extr_material_list[:10]:
        counter += 1
        print(f'{counter}. {mater}')
        c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11 = get_acts(mater)
        if c1 is not None: 
            extr_name = mater + '.csv'
            attr_to_df(c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, name=extr_name)
    print('Конец функции')
end = time.time()
print(end - start)