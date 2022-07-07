import pickle
from collections import defaultdict

def to_pickle(data, file_name):
    with open(file_name, "wb") as fp:
        pickle.dump(data, fp)

def scrape_elements(data,  table, elem_for_search):
    row_count = len(table.find_elements_by_tag_name('tr'))
    for el in elem_for_search:
        if el == 'link':
            data[el].append([i.get_attribute('href') for i in table.find_elements_by_xpath('//a[@class="cardAction openCardLink"]')])
            
        else:
            search = f'//div[@data-field="{el}"]'
            if table.find_elements_by_xpath(search):
                data[el].append([i.text for i in table.find_elements_by_xpath(search)])
            else:
                data[el].append([None for i in range(row_count)])