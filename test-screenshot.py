from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument("--kiosk")
chrome = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chrome_options)
chrome.set_window_position(0, 0)
chrome.set_window_size(800, 600)

chrome.get('https://python.org/')
chrome.save_screenshot("screenshot.png")

chrome.close()
