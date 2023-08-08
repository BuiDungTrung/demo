# import subprocess




# def run_python_file(crawl):
#     try:
#         result = subprocess.run(['python', crawl], capture_output=True, text=True, check=True)
#         # Lệnh trên chạy file Python với đường dẫn file_path, capture_output=True để bắt lấy output, text=True để trả về dạng chuỗi thay vì byte.
#         print("Output:", result.stdout)
#     except subprocess.CalledProcessError as e:
#         print("Lỗi khi chạy file:", e)
#     except FileNotFoundError:
#         print("Không tìm thấy file:", crawl)

# # Gọi hàm run_python_file và truyền vào đường dẫn đến tệp Python bạn muốn chạy.
# run_python_file(r'C:\Users\Admin\Desktop\srawl selenium\asd\123123.py')


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
import schedule
import time 
import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
# def crawl_and_store_data():
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
            CREATE TABLE IF NOT EXISTS hour (
                title TEXT,
                price TEXT,
                photo TEXT,
                nha_san_xuat TEXT,
                nuoc_san_xuat TEXT,
                thong_tin_san_pham TEXT,
                sales_in_last_24_hours TEXT,
                morning TEXT,
                afternoon TEXT,
                evening TEXT
            
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
        cursor.execute("SELECT EXISTS(SELECT 1 FROM hour WHERE title = %s)", (product_name,))
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

            # Lấy giờ trong ngày (sáng, chiều, tối) và lưu vào biến current_period
            current_hour = datetime.datetime.now().hour
            if 0 <= current_hour < 12:
                current_period = "morning"
            elif 12 <= current_hour < 18:
                current_period = "afternoon"
            else:
                current_period = "evening"

            with connection.cursor() as cursor:
                if check_product_exist(cursor, product_name):
                    # Sản phẩm đã tồn tại, cập nhật thông tin của nó
                    cursor.execute(f'''
                        UPDATE hour
                        SET price = %s, photo = %s, nha_san_xuat = %s, nuoc_san_xuat = %s, thong_tin_san_pham = %s,
                            sales_in_last_24_hours = %s, {current_period} = %s
                        WHERE title = %s;
                    ''', (gia, anh, nha_san_xuat, nuoc_san_xuat, thong_tin_san_pham, sales_in_last_24_hours, gia, product_name))
                else:
                    # Sản phẩm chưa tồn tại, thêm sản phẩm mới vào cơ sở dữ liệu
                    # Gán giá mới vào cột buổi trong ngày tương ứng với giờ hiện tại
                    cursor.execute(f'''
                        INSERT INTO hour (title, price, photo, nha_san_xuat, nuoc_san_xuat, thong_tin_san_pham, 
                            sales_in_last_24_hours, {current_period})
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    ''', (product_name, gia, anh, nha_san_xuat, nuoc_san_xuat, thong_tin_san_pham, sales_in_last_24_hours, gia))
                connection.commit()
        except Exception as e:
            print("Lỗi khi scraping sản phẩm:", str(e))
    connection.close()
    driver.quit()

# def schedule_auto_crawl():
#     # Cài đặt lịch trình hẹn giờ chạy vào phút thứ 30 trong mỗi giờ
#     schedule.every().hour.at(":50").do(crawl_and_store_data)

#     # Vòng lặp để duyệt lịch trình và thực hiện công việc đã đặt
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# # Hàm chạy chương trình tự động
# def run_auto_crawl():
#     try:
#         # Gọi hàm để đặt lịch trình hẹn giờ
#         schedule_auto_crawl()
#     except KeyboardInterrupt:
#         # Nếu bị ngắt quãng (nhấn Ctrl+C), thoát khỏi chương trình
#         print("Dừng chạy tự động.")
#         pass

# if __name__ == "__main__":
#     # Gọi hàm chạy chương trình tự động
#     run_auto_crawl()
