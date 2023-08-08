from time import sleep
import random
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import pandas as pd
from selenium import webdriver
import chromedriver_autoinstaller
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

chromedriver_autoinstaller.install()
driver = webdriver.Chrome()
url = "https://nhathuoclongchau.com.vn/duoc-my-pham"
driver.get(url)
time.sleep(1)
#cuộn trang
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(1)
# start_time = time.time()
# while time.time() - start_time <= 60:  # Keep crawling for 1 minute
#     try:
#         # Find and click the "Hiển thị thêm sản phẩm" button
#         show_more_button = driver.find_element(By.CSS_SELECTOR, ".mt-2 > .css-15sc8tc")
#         show_more_button.click()
#         time.sleep(random.randint(5, 10))  # Wait for new products to load (optional)
#     except NoSuchElementException:
#         print("No 'Hiển thị thêm sản phẩm' button found.")
#         break
#     except ElementNotInteractableException:
#         print("Unable to click the 'Hiển thị thêm sản phẩm' button.")
#         break



ten = driver.find_elements(By.CSS_SELECTOR, "div.grid-cols-2 > div h3.css-tc11gt")
gia = driver.find_elements(By.CSS_SELECTOR, "div.grid-cols-2 > div p.css-jey85n")
anh = driver.find_elements(By.CSS_SELECTOR, "div.grid-cols-2 > div img.h-\[112px\]:nth-child(3)")
link = driver.find_elements(By.CSS_SELECTOR, "div.grid-cols-2 > div h3.css-tc11gt")


for a,b,c,d  in zip(ten,gia,anh,link ):
        print("Title:", a.text)
        print("Price:", b.text)
        print("photo:",c.get_attribute("src"))
        print("link:",d.get_attribute("href"))



driver.quit()
