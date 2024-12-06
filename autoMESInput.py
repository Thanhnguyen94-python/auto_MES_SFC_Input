import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

# Cấu hình logging để ghi vào file và in ra console
logging.basicConfig(
    filename='application.log',  # Tên file log, sẽ tạo mới hoặc ghi đè lên nếu đã tồn tại
    level=logging.INFO,  # Mức độ log
    format='%(asctime)s - %(levelname)s - %(message)s',  # Định dạng log
    filemode='w'  # 'w' để ghi đè lên file mỗi lần chạy lại, 'a' để append
)

# Cấu hình console handler để log cũng xuất ra màn hình
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Ghi log mức INFO và cao hơn
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Thêm handler vào logger
logging.getLogger().addHandler(console_handler)

# Đọc dữ liệu từ file text, trả về một list các dòng
def read_data_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()

# Mở trình duyệt và điều hướng đến trang web
def open_browser(url):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    logging.info("Trình duyệt đã được mở và điều hướng đến URL.")
    return driver

# Đăng nhập vào trang web
def login_to_website(driver, username, password):
    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='GLCO003_1_USER_LU']/input"))
        )
        password_field = driver.find_element(By.XPATH, "//div[@id='GLCO003_1_PASSWORD_LU']/input")
        username_field.send_keys(username)
        password_field.send_keys(password)

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='GLCO003_1_GO_LU']//div[contains(text(), '登录')]"))
        )
        login_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Welcome')]"))
        )
        logging.info("Đăng nhập thành công.")
    except Exception as e:
        logging.error(f"Lỗi đăng nhập: {e}")

# Nhấn vào phần tử "Xử lý bất thường SFC" và đợi trang tải
def click_sfc_element(driver):
    try:
        sfc_image = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//td[normalize-space(text())='Xử lý bất thường SFC']"))
        )
        sfc_image.click()
        logging.info("Đã nhấn vào phần tử 'Xử lý bất thường SFC'!")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Vui lòng quét...')]"))
        )
        logging.info("Trang đã tải xong!")
    except Exception as e:
        logging.error(f"Không thể tìm thấy hoặc click vào phần tử: {e}")

# Nhập dữ liệu mã đơn vào trường nhập liệu
def input_PO_number_to_web(driver, PO_number):
    try:
        input_field = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='ZBCO083_8_INPUT_LU']//input"))
        )
        input_field.clear()
        input_field.send_keys(PO_number)
        input_field.send_keys(Keys.RETURN)
        time.sleep(1)
        logging.info(f"Đã nhập mã đơn: {PO_number}")
    except Exception as e:
        logging.error(f"Không thể nhập dữ liệu vào trường nhập liệu: {e}")

def input_text_to_web(driver, line):
    try:
        input_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='ZBPD124_11_SFC_LU']//input"))
        )
        input_field.clear()
        input_field.send_keys(line)
        input_field.send_keys(Keys.RETURN)
        time.sleep(1)
        logging.info(f"Đã nhập text thành công: {line}")
    except Exception as e:
        logging.error(f"Không thể nhập dữ liệu text vào trường nhập liệu: {e}")

# Hàm gọi từ giao diện GUI
def start_process():
    PO_number = po_number_entry.get()
    if not PO_number:
        messagebox.showerror("Lỗi", "Vui lòng nhập mã PO!")
        logging.error("Mã PO không được nhập.")
        return
    username = user_entry.get()
    if not username:
        messagebox.showerror("Lỗi", "Vui lòng nhập User !")
        logging.error("User không được nhập.")
        return
    password = pass_entry.get()
    if not password:
        messagebox.showerror("Lỗi", "Vui lòng nhập mật khẩu!")
        logging.error("Mật khẩu không được nhập.")
        return

    file_path = "./list.txt"
    url = 'http://172.16.250.202:8081/smartMes/mesv/qj.ui/qjui/index.html'  # URL của trang web

    try:
        driver = open_browser(url)
        time.sleep(2)

        login_to_website(driver, username, password)
        click_sfc_element(driver)
        input_PO_number_to_web(driver, PO_number)

        lines = read_data_from_file(file_path)
        for line in lines:
            input_text_to_web(driver, line)

        messagebox.showinfo("Hoàn thành", "Quá trình đã hoàn thành. Bạn có thể đóng trình duyệt.")
        logging.info("Quá trình đã hoàn thành.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
        logging.error(f"Đã xảy ra lỗi trong quá trình thực thi: {e}")
    finally:
        driver.quit()
        logging.info("Trình duyệt đã đóng.")

# Tạo giao diện GUI
root = tk.Tk()
root.title("Tự động nhập xử lý bất thường.")

# Cấu hình cửa sổ
root.geometry("600x400")

# Tiêu đề
title_label = tk.Label(root, text="Nhập danh sách QR để xử lý bất thường SFC:", font=("Arial", 16))
title_label.pack(pady=20)

# Chỗ nhập PO Number
po_number_label = tk.Label(root, text="Mã mã đơn:")
po_number_label.pack()

po_number_entry = tk.Entry(root, font=("Arial", 14))
po_number_entry.pack(pady=10)

# Chỗ nhập User 
user_label = tk.Label(root, text="User:")
user_label.pack()

user_entry = tk.Entry(root, font=("Arial", 14))
user_entry.pack(pady=10)

# Chỗ nhập pass
pass_label = tk.Label(root, text="pass:")
pass_label.pack()

pass_entry = tk.Entry(root, font=("Arial", 14))
pass_entry.pack(pady=10)

# Nút bắt đầu quá trình
start_button = tk.Button(root, text="Bắt đầu", font=("Arial", 14), command=start_process)
start_button.pack()

# Chạy ứng dụng
root.mainloop()
