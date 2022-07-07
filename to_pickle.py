import pickle
from collections import defaultdict

def to_pickle(data):
    with open("data", "wb") as fp:
        pickle.dump(data, fp)

def scrape_elements(data,  table):
    elem_for_search = [
        "case_user_doc_number",
        "adm_case_user_name",
        "case_common_parts_law_article",
        "case_user_entry_date",
        "case_doc_subject_rf",
        "case_user_doc_court",
        "adm_case_user_name",
        "case_user_doc_result",
        "case_user_doc_result_date"
    ]

    row_count = len(table.find_elements_by_tag_name('tr'))
    for el in elem_for_search:
        search = f'//div[@data-field="{el}"]'
        if table.find_elements_by_xpath:
            data[el].append([i.text for i in table.find_elements_by_xpath(search)])
        else:
            data[el].append([None for i in range(row_count)])

