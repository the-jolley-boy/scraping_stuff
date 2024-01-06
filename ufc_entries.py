################################################################################################

# Author: Kian Jolley

# This bot is to only be used by allowed individuals 

################################################################################################

import os
import discord
from discord import app_commands
import time
import asyncio
import io
import random
import names
import datetime
from itertools import cycle, islice
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Bot Token
token = ''
intents = discord.Intents().all()
intents.members = True
intents.guilds = True

class Client(discord.Client):
    def __init__(self):
        super().__init__(intents = intents)
        self.synced = False
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await client.sync()
            self.synced = True
        print(f'{self.user} has connected to Discord!')

Client = Client()
client = app_commands.CommandTree(Client)

@client.command(name = "ufcenrollmsg", description = "100 proxies & 100 gmails or 1 catchall. Separate input with comma no spaces.")
async def ufcenrollmsg(interaction: discord.Interaction, proxy: str, emails: str):

    await interaction.response.send_message("Submitting entries now...")

    loop = asyncio.get_running_loop()
    time, issues = await loop.run_in_executor(None, msg, proxy, emails)
    i = ', '.join([str(item) for item in issues])
    await interaction.channel.send("Finished Site #1 in " + str(time) + " seconds.\nYou also had a failed entry on entries " + str(i) + ".")

@client.command(name = "ufcenrollufc", description = "100 proxies & 100 gmails or 1 catchall. Separate input with comma no spaces.")
async def ufcenrollufc(interaction: discord.Interaction, proxy: str, emails: str):

    await interaction.response.send_message("Submitting entries now...")

    loop = asyncio.get_running_loop()
    time, issues = await loop.run_in_executor(None, ufc, proxy, emails)
    i = ', '.join([str(item) for item in issues])
    await interaction.channel.send("Finished Site #2 in " + str(time) + " seconds.\nYou also had a failed entry on entries " + str(i) + ".")

def msg(proxy, emails):
    # First sort if gmails or catchall
    isgmail = 0
    emaillist = []
    proxylist = []
    issues = []
    if "@gmail.com" in emails:
        isgmail = 1
        emaillist = emails.split(",")

    pl = proxy.split(",")

    proxylist = list(islice(cycle(pl), 25))

    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-logging')
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    opts.add_experimental_option("useAutomationExtension", False) 
    opts.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"

    # For Browser 1
    browser1 = webdriver.Chrome(options=opts, service=Service(ChromeDriverManager().install()))

    time = datetime.datetime.now()

    i = 0
    while i < 25:

        pxy = proxylist[i].split(":")

        browser1.proxy = {
            'http': f'http://{pxy[2]}:{pxy[3]}@{pxy[0]}:{pxy[1]}',
            'https': f'http://{pxy[2]}:{pxy[3]}@{pxy[0]}:{pxy[1]}',
        }

        browser1.get("https://msg-wmzqo.formstack.com/forms/ufc_295")

        try:
            element = WebDriverWait(browser1, 10).until(
                EC.presence_of_element_located((By.ID, "field147946152-first"))
            )
        
            first_name = browser1.find_element(By.ID, "field147946152-first")
            last_name = browser1.find_element(By.ID, "field147946152-last")
            email = browser1.find_element(By.ID, "field147946153")
            submit = browser1.find_element(By.ID, "fsSubmitButton5363561")

            first = names.get_first_name()
            last = names.get_last_name()
            first_name.send_keys(first)
            last_name.send_keys(last)

            if isgmail == 0:
                email.send_keys(first + last + emails)
            else:
                email.send_keys(emaillist[i])

            submit.click()

            wait = WebDriverWait(browser1, 10)
            wait.until(lambda driver: browser1.current_url != "https://msg-wmzqo.formstack.com/forms/ufc_295")

            i = i + 1

        except Exception as e:
            print("Exception: " + str(e) + "\nMay be due to a proxy being banned on the site.")
            issues.append(i)

            i = i + 1

    browser1.close()
    browser1.quit()
    print(datetime.datetime.now() - time)

    return (datetime.datetime.now() - time), issues

def ufc(proxy, emails):
    # First sort if gmails or catchall
    isgmail = 0
    emaillist = []
    proxylist = []
    issues = []
    if "@gmail.com" in emails:
        isgmail = 1
        emaillist = emails.split(",")

    pl = proxy.split(",")

    proxylist = list(islice(cycle(pl), 25))

    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-logging')
    opts.add_argument('--disable-gpu')
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    opts.add_experimental_option("useAutomationExtension", False) 
    opts.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"

    # For Browser 2
    browser2 = webdriver.Chrome(options=opts, service=Service(ChromeDriverManager().install()))

    time = datetime.datetime.now()
    browser2.set_page_load_timeout(6)

    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", 
                "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", 
                "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", 
                "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", 
                "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
                "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", 
                "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

    i = 0
    while i < 25:

        pxy = proxylist[i].split(":")

        browser2.proxy = {
            'http': f'http://{pxy[2]}:{pxy[3]}@{pxy[0]}:{pxy[1]}',
            'https': f'http://{pxy[2]}:{pxy[3]}@{pxy[0]}:{pxy[1]}',
        }

        try:
            browser2.get("https://form.jotform.com/231917397920161")
        except TimeoutException:
            browser2.execute_script("window.stop();")

        try:
            element = WebDriverWait(browser2, 10).until(
                EC.presence_of_element_located((By.ID, "input_3"))
            )

            first_name = browser2.find_element(By.ID, "input_3")
            last_name = browser2.find_element(By.ID, "input_4")
            email = browser2.find_element(By.ID, "input_5")
            country = browser2.find_element(By.ID, "input_6")
            state = browser2.find_element(By.ID, "input_7")
            checkbox = browser2.find_element(By.ID, "input_9_0")
            submit = browser2.find_element(By.ID, "input_2")

            first = names.get_first_name()
            last = names.get_last_name()
            first_name.send_keys(first)
            last_name.send_keys(last)

            if isgmail == 0:
                email.send_keys(first + last + emails)
            else:
                email.send_keys(emaillist[i])

            country.send_keys("United States")
            state.send_keys(random.choice(states))

            checkbox.click()

            submit.click()

            wait = WebDriverWait(browser2, 10)
            wait.until(lambda driver: browser2.current_url != "https://form.jotform.com/231917397920161")

            i = i + 1

        except Exception as e:
            print("Exception: " + str(e) + "\nMay be due to a proxy being banned on the site.")
            issues.append(i)

            i = i + 1

    browser2.close()
    browser2.quit()
    print(datetime.datetime.now() - time)
    return (datetime.datetime.now() - time), issues

Client.run(token)