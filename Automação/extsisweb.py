import selenium 
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)
driver.implicitly_wait(20)
driver.maximize_window()
# link
driver.get("http://operacao-sisweb/Unificado/TLV/Session/Login?returnUrl=/Unificado/TLV/")

# login
driver.find_element(By.XPATH, 
    '/html/body/div[4]/div[1]/div/form/div/div[1]/div/input').send_keys("TR749542")
driver.find_element(By.XPATH, 
    '/html/body/div[4]/div[1]/div/form/div/div[2]/div/input').send_keys("7tysd7ysgsv9s")
driver.find_element(By.XPATH,
    '/html/body/div[4]/div[1]/div/form/div/div[3]/div/button').click()

# Relatorio Base Geral
driver.find_element(By.XPATH,
    '/html/body/div[4]/div[1]/ul/li[4]/ul/li[1]/a').click()

time.sleep(3)

# Data inicial
driver.find_element(By.XPATH,
    '/html/body/div[4]/form/div[5]/div[1]/div/div/input').send_keys(datetime.today().strftime('%d/%m/%Y'))

# Data Final
driver.find_element(By.XPATH,
    '/html/body/div[4]/form/div[5]/div[2]/div/div/input').send_keys(datetime.today().strftime('%d/%m/%Y'))

driver.find_element(By.XPATH,
    '/html/body').send_keys(Keys.SPACE)

# Relatorio Historico Final
driver.find_element(By.XPATH,
    '/html/body/div[4]/form/div[11]/div/div/button[2]').click()

time.sleep(10)
driver.quit()