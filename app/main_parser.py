from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from xvfbwrapper import Xvfb
import datetime
import exceptions


def login(username, password):
    vdisplay = Xvfb()
    vdisplay.start()

    fx_options = Options()
    fx_options.add_argument("--no-sandbox")
    fx_options.add_argument("--disable-setuid-sandbox")
    fx_options.headless = True
    driver = webdriver.Firefox(firefox_options=fx_options)

    try:
        driver.get("https://lk.sut.ru/cabinet/")
    except Exception as ex:
        driver.close()
        vdisplay.stop()
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

    email_field = driver.find_element_by_id("users")
    email_field.send_keys(username)

    password_field = driver.find_element_by_id("parole")
    password_field.send_keys(password)

    login_button = driver.find_element_by_id("logButton")
    login_button.click()

    driver.get("https://lk.sut.ru/cabinet/?login=yes")

    try:
        schedule_button = driver.find_element_by_id("heading1")
        schedule_button.click()
    except Exception as ex:
        print(f'An exception of type {type(ex).__name__} occurred. Arguments:\n{ex.args!r} при входе на расписание')
        driver.close()
        vdisplay.stop()
        raise exceptions.NotBonchUser

    parse_button = driver.find_element_by_id("menu_li_6118")
    parse_button.click()

    current_date_time = datetime.datetime.now()
    current_time = current_date_time.time()

    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Начать занятие"))).click()
    except Exception as ex:
        print(f'{username} не нашёл кнопку в {current_time}, трабл {type(ex).__name__}')
        return
    finally:
        driver.close()
        vdisplay.stop()
    print(f'{username} нашёл кнопку в {current_time}')
    return
