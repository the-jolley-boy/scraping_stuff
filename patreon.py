from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import random
import psycopg2
from psycopg2 import sql
from string import ascii_lowercase as alc

from config import DBTable, DBHost, DBUsr, DBPass, DBPort

def getPatreons(search):

    opts = Options()
    # opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-logging')
    opts.add_argument('--disable-gpu')
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    opts.add_experimental_option("useAutomationExtension", False) 
    opts.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"

    browser = webdriver.Chrome(options=opts, service=Service(ChromeDriverManager().install()))
    browser.set_page_load_timeout(6)

    patreon_dict = {}

    i = 1
    while i < 4:

        pxy = random.choice(proxylist).split(":")

        browser.proxy = {
                'http': f'http://{pxy[2]}:{pxy[3]}@{pxy[0]}:{pxy[1]}',
                'https': f'https://{pxy[2]}:{pxy[3]}@{pxy[0]}:{pxy[1]}'
            }

        try:
            if i == 1:
                browser.get("https://www.patreon.com/search?q=" + search)
            else:
                browser.get("https://www.patreon.com/search?q=" + search + "&p=" + str(i))
        except TimeoutException:
            browser.execute_script("window.stop();")

        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="renderPageContentWrapper"]/div/div[2]'))
            )

            x = 1
            while True:
                try:
                    link = browser.find_element(By.XPATH, '//*[@id="renderPageContentWrapper"]/div/div[2]/div[' + str(x) + ']/a').get_attribute('href')
                    name = browser.find_element(By.XPATH, '//*[@id="renderPageContentWrapper"]/div/div[2]/div[' + str(x) + ']/a/div[2]/span').text
                    desc = browser.find_element(By.XPATH, '//*[@id="renderPageContentWrapper"]/div/div[2]/div[' + str(x) + ']/a/div[2]/div[1]/p').text
                    post = browser.find_element(By.XPATH, '//*[@id="renderPageContentWrapper"]/div/div[2]/div[' + str(x) + ']/a/div[2]/div[2]/p[1]').text
                    parteon_id = link.replace("https://www.patreon.com/", "")
                    try:
                        memb = browser.find_element(By.XPATH, '//*[@id="renderPageContentWrapper"]/div/div[2]/div[' + str(x) + ']/a/div[2]/div[2]/p[3]').text
                    except:
                        memb = "Unknown member amount."

                    list_for_dict = [name, desc, post, memb, link]

                    if name not in patreon_dict:
                        patreon_dict[parteon_id] = list_for_dict

                    x = x + 1
                except NoSuchElementException:
                    break

            i = i + 1
        except Exception as e:
            print("Exception: " + str(e) + "\nMay be due to a proxy being banned on the site. \nHappened with search: " + search + "\nOn page: " + str(i))
            i = i + 1

    return patreon_dict

def addToDb(patreon_dict):
    try:
        conn = psycopg2.connect(dbname = DBTable, user = DBUsr, password = DBPass, host = DBHost, port = DBPort)
        curr = conn.cursor()

        #insert into the db unless already in the db in that case update
        postgreSQL_upload_Query = sql.SQL("INSERT INTO patreon (patreon_id, name, description, posts, members, link) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (patreon_id) DO NOTHING")

        #data for the %s values
        for key, value in patreon_dict.items():
            data = (key, value[0], value[1], value[2], value[3], value[4])
            curr.execute(postgreSQL_upload_Query, data)

        conn.commit()
        conn.close()
    except Exception as e:
        print("Error: " + str(e))

# Scraping purely through their search feature, can be customized however, this is just to pull a random large set, around 20-30k total.
def main():
    for i in alc:
        for j in alc:
            patreon_dict = getPatreons(i + j)
            print("Search Complete for " + i + j + ", now adding to DB.")
            addToDb(patreon_dict)
            print("Added to DB.")

if __name__ == "__main__":
    main()