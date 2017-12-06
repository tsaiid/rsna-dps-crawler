import sys, re, os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class all_images_loaded(object):
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

poster_id = 'BR100-ED-X'
m = re.search(r'(\w+)(\d+).+', poster_id)
subspecialty, subspecialty_id = m.group(1), m.group(2)

#chrome.get('https://python.org/')
chrome.get('https://dps.rsna.org/media/BR100-ED-X/presentation/')

#sys.exit(1)

title = chrome.title
viewpost_element = chrome.find_element_by_id("SGT_viewport")

#chrome.implicitly_wait(10)

prev_sld_id = ""
reach_slides_end = False
while not reach_slides_end:
    try:
        WebDriverWait(chrome, 10).until(all_images_loaded())
    finally:
        sld_div = chrome.find_element_by_xpath("//div[starts-with(@id, 'sld')]")
        curr_sld_id = sld_div.get_attribute("id")
        if curr_sld_id != prev_sld_id:
            chrome.save_screenshot("{}.png".format(curr_sld_id))
            viewpost_element.click()
            prev_sld_id = curr_sld_id
        else:
            reach_slides_end = True

chrome.close()
