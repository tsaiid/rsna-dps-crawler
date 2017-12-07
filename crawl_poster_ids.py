"""
Crawl RSNA DPS Poster ids.
"""

import argparse
import configparser
import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test",
                        help="run in test mode; download only 3 pages",
                        action="store_true")
    args = parser.parse_args()

    # read config.ini
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    username = cfg['dps.rsna.org']['Username']
    password = cfg['dps.rsna.org']['Password']

    dps_url = 'https://dps.rsna.org/'

    # prepare selenium
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-extensions')

    chrome = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chrome_options)

    # do crawling
    chrome.get(dps_url)
    wait = WebDriverWait(chrome, 30)

    posters = {}

    # check login
    try:
        username_input = chrome.find_element_by_id("username")
        password_input = chrome.find_element_by_id("password")
        login_btn = chrome.find_element_by_id("loginBtn")

        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)
        login_btn.click()
    finally:
        pass

    try:
        login_page = chrome.find_element_by_tag_name('html')
        wait.until(EC.staleness_of(login_page))
    finally:
        pass

    reach_end_page = False
    page_counter = 0   # for test mode use
    while not reach_end_page:
        try:
            #list_element = chrome.find_element_by_id('list')
            #wait.until(EC.staleness_of(list_element))
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.loadingGIF')))
            wait.until(EC.element_to_be_clickable((By.ID, 'qa_thumbnails')))
            #next_page_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'ul#qa_pagination li._nextLink')))
        finally:
            if args.test:
                page_counter += 1
                if page_counter > 3:
                    break

            id_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='list']//span/strong")))
            title_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='list']//div/strong")))
            #curr_page_ids = tuple(id.text for id in chrome.find_elements_by_xpath("//div[@id='list']//span/strong"))
            curr_page_ids = tuple(id.text for id in id_elements)
            #curr_page_titles = tuple(title.text for title in chrome.find_elements_by_xpath("//div[@id='list']//div/strong"))
            curr_page_titles = tuple(title.text for title in title_elements)
            posters = {**posters, **dict(zip(curr_page_ids, curr_page_titles))}

            #print(posters)
            # check if the last page
            curr_page = chrome.find_element_by_css_selector('ul#qa_pagination span._page').text
            max_page = chrome.find_element_by_css_selector('ul#qa_pagination span._max').text
            print('curr_page: {} / max_page: {}'.format(curr_page, max_page))
            if curr_page == max_page:
                break

            chrome.execute_script('document.querySelector("li._nextLink").click();')

    #chrome.close()
    #print(posters)
    poster_csv_path = os.path.join(os.path.dirname(__file__), 'poster.csv')
    write_dict_to_csv(poster_csv_path, posters)
    #print(page_counter)

def write_dict_to_csv(csv_file, dict_data):
    """
    Write dict object to csv file
    """
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['poster_id', 'title'])
            writer.writeheader()
            for key, value in dict_data.items():
                writer.writerow({'poster_id': key, 'title': value})
    except IOError:
        print('I/O error', csv_file)
    return


if __name__ == '__main__':
    main()
