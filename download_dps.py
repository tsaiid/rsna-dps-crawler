"""
Download RSNA DPS by a given poster id.
"""

import argparse
import sys
import re
import os
import pathlib
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class AllImagesLoaded(object):
    """An expectation for checking that an element has a particular css class.

    locator - used to find the element
    returns the WebElement once it has the particular css class
    """
#  def __init__(self, locator, css_class):
#    self.locator = locator
#    self.css_class = css_class

    def __call__(self, driver):
        return driver.execute_script("""
var allLoaded = true;
var imgs = document.getElementsByTagName("img");
for (i = 0; i < imgs.length; i++) {
  if (!imgs[i].complete || imgs[i].naturalHeight === 0) {
    allLoaded = false;
    break;
  }
}
return allLoaded;
""")

def main():
    """
    Main function
    """
    # parse poster id
    parser = argparse.ArgumentParser()
    parser.add_argument('poster_id')
    parser.add_argument("-t", "--test", help="run in test mode; download only 3 slides", action="store_true")
    args = parser.parse_args()

    #poster_id = 'BR100-ED-X'
    poster_id = args.poster_id
    match = re.search(r'([a-zA-Z]+)(\d+).+', poster_id)
    subspecialty, subspecialty_id = match.group(1), match.group(2)
    poster_url = 'https://dps.rsna.org/media/{}/presentation/'.format(poster_id)

    # check if the poster exists
    r = requests.get(poster_url)
    if r.status_code != 200:
        print("The poster ({}) does not exist.".format(poster_id))
        return r.status_code

    # prepare selenium
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("--kiosk")

    #capa = DesiredCapabilities.CHROME
    #capa["pageLoadStrategy"] = "normal"

    #chrome = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chrome_options, desired_capabilities=capa)
    chrome = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chrome_options)
    #chrome.set_window_position(0, 0)
    #chrome.set_window_size(800, 800)

    # do crawling
    chrome.get(poster_url)

    # mkdirs
    downloaded_poster_path = os.path.join(os.path.dirname(__file__), '{}/{} {}'.format(subspecialty, poster_id, chrome.title))
    pathlib.Path(downloaded_poster_path).mkdir(parents=True, exist_ok=True)

    #chrome.close()
    #sys.exit(1)

    viewpost_element = chrome.find_element_by_id("SGT_viewport")

    prev_sld_id = ""
    reach_slides_end = False
    slide_counter = 0   # for test mode use
    while not reach_slides_end:
        try:
            WebDriverWait(chrome, 10).until(AllImagesLoaded())
        finally:
            if args.test:
                slide_counter += 1
                if slide_counter > 3:
                    break
            
            sld_div = chrome.find_element_by_xpath("//div[starts-with(@id, 'sld')]")
            curr_sld_id = sld_div.get_attribute("id")
            if curr_sld_id != prev_sld_id:
                downloaded_sld_path = os.path.join(downloaded_poster_path, "{}.png".format(curr_sld_id))
                chrome.save_screenshot(downloaded_sld_path)
                viewpost_element.click()
                prev_sld_id = curr_sld_id
            else:
                reach_slides_end = True

    chrome.close()

if __name__ == '__main__':
    main()
