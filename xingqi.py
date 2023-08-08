from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
import psycopg2
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import codecs

if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

chromedriver_autoinstaller.install()
driver = webdriver.Chrome()
url = "https://thuocsi.vn/products"

connection = psycopg2.connect(
    host="localhost",
        database="dc",
        user="postgres",
        password="1"
)

with connection.cursor() as cursor:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS xingqi (
            title TEXT,
            price TEXT,
            photo TEXT,
            nha_san_xuat TEXT,
            nuoc_san_xuat TEXT,
            thong_tin_san_pham TEXT,
            sales_in_last_24_hours TEXT,
            month_1 TEXT,
            month_2 TEXT,
            month_3 TEXT,
            month_4 TEXT,
            month_5 TEXT,
            month_6 TEXT,
            month_7 TEXT,
            month_8 TEXT,
            month_9 TEXT,
            month_10 TEXT,
            month_11 TEXT,
            month_12 TEXT
        )
    ''')
    connection.commit()

# Mở đường dẫn URL
driver.get(url)
try:
    wait = WebDriverWait(driver, 10)
    click_login = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".MuiGrid-root:nth-child(1) > .styles_link__t2Gkc > .MuiTypography-root")))
    click_login.click()

    username_input = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".MuiFormControl-root:nth-child(1) .MuiInputBase-input")))
    password_input = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input.MuiInputBase-inputAdornedEnd")))

    username_input.send_keys("0328479814")
    password_input.send_keys("trungdc@123")

    login_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".styles_btn_register__zCg7F > .MuiButton-label")))
    login_button.click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".styles_root__yHa_F > .styles_tab_panel__NAwAa")))
except (NoSuchElementException, TimeoutException) as e:
    print("Lỗi khi đăng nhập:", str(e))

    connection.commit()


def extract_product_info(html):
    soup = BeautifulSoup(html, 'html.parser')

    manufacturer = "N/A"
    country_of_origin = "N/A"
    product_info = "N/A"
    sales_in_last_24_hours = "N/A"

    # Find the manufacturer info and extract data if available
    manufacturer_info = soup.find('div', class_='styles_warpper____CUU')
    if manufacturer_info:
        manufacturer_element = manufacturer_info.find('a', class_='styles_manufactureInfoLink__0pU6d')
        if manufacturer_element:
            manufacturer = manufacturer_element.text

    country_of_origin_info = soup.find('div', class_='styles_warpper__a1pGy')
    if country_of_origin_info:
        country_of_origin_element = country_of_origin_info.find('p',
                                                                class_='MuiTypography-root styles_manufactureInfoLink__NlYlw MuiTypography-body1')
        if country_of_origin_element:
            country_of_origin = country_of_origin_element.text

    product_info_element = soup.find('div', class_='styles_content__L0lSp')
    if product_info_element:
        product_info = product_info_element.text.strip()

    sales_element = soup.find('p', class_='MuiTypography-root styles_nameDescNumber__JUiEI MuiTypography-body1')
    if sales_element:
        sales_in_last_24_hours = sales_element.text.strip()

    product_name_element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'p.titleProduct,p.styles_last_breadcrumb__c7IQm')))
    product_name = product_name_element.text

    return manufacturer, country_of_origin, product_info, sales_in_last_24_hours, product_name


num_pages_to_scrape = 1
link = []
for page_num in range(1, num_pages_to_scrape + 1):
    url = f"https://thuocsi.vn/products?page={page_num}"
    driver.get(url)
    l = driver.find_elements(By.CSS_SELECTOR,
                             ".style_product_grid_wrapper__lYnBj > .MuiGrid-root > div span > .styles_mobile_rootBase__8z7PQ")
    for i in l:
        lin = i.get_attribute('href')
        link.append(lin)


def check_product_exist(cursor, product_name):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM xingqi WHERE title = %s)", (product_name,))
    return cursor.fetchone()[0]

# Thêm các sản phẩm vào cơ sở dữ liệu với giá mới lưu vào 12 tháng gần nhất
for a in link:
    try:
        driver.get(a)
        ten = ""
        gia = ""
        anh = ""
        nha_san_xuat = ""
        nuoc_san_xuat = ""
        thong_tin_san_pham = ""
        sales_in_last_24_hours = ""
        product_name = ""

        try:
            html = driver.page_source
            nha_san_xuat, nuoc_san_xuat, thong_tin_san_pham, sales_in_last_24_hours, product_name = extract_product_info(
                html)
        except NoSuchElementException:
            pass

        try:
            ten = driver.find_element(By.CSS_SELECTOR, 'p.titleProduct,p.styles_last_breadcrumb__c7IQm').text
        except NoSuchElementException:
            ten = "N/A"

        try:
            gia = driver.find_element(By.CSS_SELECTOR, 'div.styles_deal_price__HiSOK,span.styles_deal_price__HiSOK').text
        except NoSuchElementException:
            gia = "N/A"

        try:
            anh = driver.find_element(By.CSS_SELECTOR, 'img.styles_imageMain__UQ9fH').get_attribute('src')
        except NoSuchElementException:
            anh = "N/A"

        with connection.cursor() as cursor:
            if check_product_exist(cursor, product_name):
                # Sản phẩm đã tồn tại, cập nhật thông tin của nó
                cursor.execute('''
                           UPDATE xingqi
                           SET price = %s, photo = %s, nha_san_xuat = %s, nuoc_san_xuat = %s, thong_tin_san_pham = %s,
                               sales_in_last_24_hours = %s, month_12 = month_11, month_11 = month_10, month_10 = month_9,
                               month_9 = month_8, month_8 = month_7, month_7 = month_6, month_6 = month_5,
                               month_5 = month_4, month_4 = month_3, month_3 = month_2, month_2 = month_1, month_1 = %s
                           WHERE title = %s;
                       ''', (
                gia, anh, nha_san_xuat, nuoc_san_xuat, thong_tin_san_pham, sales_in_last_24_hours, gia, product_name))
            else:
                # Sản phẩm chưa tồn tại, thêm sản phẩm mới vào cơ sở dữ liệu
                cursor.execute('''
                                INSERT INTO xingqi (title, price, photo, nha_san_xuat, nuoc_san_xuat, thong_tin_san_pham, 
                                    sales_in_last_24_hours, month_1, month_2, month_3, month_4, month_5, month_6,
                                    month_7, month_8, month_9, month_10, month_11, month_12)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                            ''', (
                    product_name, gia, anh, nha_san_xuat, nuoc_san_xuat, thong_tin_san_pham, sales_in_last_24_hours,
                    gia, "", "", "", "", "", "", "", "", "", "", ""))
            connection.commit()
    except Exception as e:
        print("Lỗi khi scraping sản phẩm:", str(e))

connection.close()
driver.quit()