# -*- coding: utf-8 -*-

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains, Keys
import uuid


from selenium_stealth import stealth

import pandas as pd

from selenium.webdriver.chrome.service import Service
from time import sleep
from lxml import html
import os

class CommonsImazit():
    # print(like[0].get_attribute("outerHTML"))
    # //*[local-name() = 'svg']
    # //*[local-name() = 'svg']/ancestor::div
    # //*[local-name() = 'svg']/div::div
    def test(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--log-level=3")
        self.options.add_argument("--remote-debugging-port=9222")
        self.options.add_argument("--disable-browser-side-navigation")
        self.options. add_argument("--blink-settings=imagesEnabled=false")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--no-first-run")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.62 Safari/537.36')
        self.options.page_load_strategy = 'normal'

        # Add realistic browser preferences
        prefs = {
            "download.default_directory": "Downloads",
            "intl.accept_languages": "en-US,en;q=0.9",
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }
        self.options.add_experimental_option("prefs", prefs)

        # Disable browser notifications
        self.options.add_argument("--disable-notifications")

        # Disable browser password saving
        self.options.add_argument('--no-service-autorun')
        self.options.add_argument('--password-store=basic')

        # self.driver.execute_script("window.open('https://restorecord.com/');")
        self.driver.get("https://restorecord.com/")
        input()
        self.driver.save_screenshot("print.png")

        time.sleep(600)

        # self.driver.switch_to.window(self.driver.window_handles[-1])
        
        
    def wait_load(self, xpath, driver, timeout = 5*60):
        loaded = False
        last_time = time.time()
        while not loaded:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                if (len(elements)>0):
                    loaded = True
                    print("elements case")
            except:
                loaded = False
                print("except case")
                
            verify_time = ( time.time() - last_time) >= timeout
            # print(last_time - time.time())
            if (verify_time):
                print("time case")
                return False
                
        return loaded

class InstagramBot():
    
    def __init__(self):
        cm = CommonsImazit()
        self.wait_load = cm.wait_load
        self.url= "https://www.instagram.com"
        # BANCO DE DADOS
        self._file_db = "./database.xlsx"
        try:
            self.df = pd.read_excel(self._file_db)
        except:
            self.df = pd.DataFrame()
            self.df.to_excel(self._file_db, engine='xlsxwriter', index=0)
    
    
        self.options = webdriver.ChromeOptions()

        # options.add_experimental_option('--excludeSwitches', ['disable-logging'])
        self.options.add_argument('--log-level=3')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--ignore-certificate-errors-spki-list')
        self.options.add_argument("--start-maximized")
    def start_webdriver(self, userdata):
        service = Service(ChromeDriverManager().install())
        
        # self.options.add_argument("--window-position=2000,0")
        # self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--headless")
        
        self.options.add_argument(userdata)
        
        self.driver = webdriver.Chrome(options=self.options, service=service)
        
        self.actions = ActionChains(self.driver)


        stealth(self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
            
        # self.driver.set_window_size(1920, 1080)
        # self.driver.set_page_load_timeout(30)
        
        # self.capa = DesiredCapabilities.CHROME
        # self.capa["pageLoadStrategy"] = "none"

        # self.driver = webdriver.Chrome(desired_capabilities=capa)
        # self.driver.set_page_load_timeout(10)c
    
    def set_login(self, login: str, password: str):
        self.login = login
        self.password = password
        

    def run_login(self) -> bool:
        
        _uuid = uuid.uuid4()
        is_user_in_db = self.find_user_in_db(self.login)
        print(is_user_in_db)
        if (is_user_in_db != None):
            _uuid = self.find_user_in_db(self.login)
        
        self.start_webdriver(userdata = f'--user-data-dir={os.getcwd()}/userdata/{_uuid}')
        
        def is_logged() -> bool:
            if self.wait_load(".//*[local-name() ='svg' and @aria-label = 'Instagram']", self.driver, 10) == True:
                return True

        self.driver.get(self.url)
        
        if (is_logged()):
            return self.driver.quit()
        
        self.wait_load(".//input[@name = 'username']", self.driver, 60)
        
        username = self.driver.find_element(By.XPATH, ".//input[@name = 'username']")
        username.send_keys(self.login)
        
        password = self.driver.find_element(By.XPATH, ".//input[@name = 'password']")
        password.send_keys(self.password)
        
        login = self.driver.find_element(By.XPATH, ".//div//button[@type = 'submit']")
        login.click()
        
        print("Situação de login:", is_logged())
        
        if (is_user_in_db == None):
            self.save_user_in_db(uuid=_uuid)
        
        return self.driver.quit()
    
    def find_user_in_db(self, login):
        filtered = self.df.query("login == @login")
        if (len(filtered) == 0):
            return None
        else:
            return filtered["uuid"].iloc[0]
    
    def save_user_in_db(self, uuid: str):
        # SAVE THE UUID
        new_df = pd.DataFrame(columns=["login", "uuid"], data=[[self.login, uuid]])
        self.df = pd.concat([self.df, new_df])
        os.remove(self._file_db)
        self.df.to_excel(self._file_db, sheet_name='users', index=0)
    
    def run_likes(self, login: str,  username: str):
        _uuid = uuid.uuid4()
        is_user_in_db = self.find_user_in_db(login)
        if (is_user_in_db != None):
            _uuid = self.find_user_in_db(login)
            self.start_webdriver(userdata = f'--user-data-dir={os.getcwd()}/userdata/{_uuid}')
        else:
            return {
                "status": "User are not authenticated."
            }
            
        self.driver.get(f"{self.url}/{username}")

        self.wait_load(".//div/div/img", self.driver, 5)
        
        self.wait_load("(.//a[(contains(@href, '/p/') or contains(@href, '/reel/'))])", self.driver)
        time.sleep(5)

        posts = self.driver.find_elements(By.XPATH, "(.//a[(contains(@href, '/p/') or contains(@href, '/reel/'))])")
        
        post_links = list(post.get_attribute("href") for post in posts)
        post_links = [post_links[0]]
        
        log = {}
        log[username] = []
        for post in post_links:
            self.driver.get(post)
            
            self.wait_load(".//button/parent::div/span//*[local-name() = 'svg' and @aria-label='Like']/parent::*/parent::*/parent::*", self.driver,)
            try:
                time.sleep(5)
                
                like_button = self.driver.find_element(By.XPATH, ".//button/parent::div/span//*[local-name() = 'svg' and @aria-label='Like']/parent::*/parent::*/parent::*")
                self.actions.move_to_element(like_button).perform()
                like_button.click()
                
                self.wait_load(".//button/parent::div/span//*[local-name() = 'svg' and @aria-label='Unlike']/parent::*/parent::*/parent::*", self.driver)
                
                log[username].append({
                    "post": post,
                    "status": "Liked"
                })
                
                time.sleep(5)
                
            except:
                try:
                    unlike_button = self.driver.find_element(By.XPATH, ".//button/parent::div/span//*[local-name() = 'svg' and @aria-label='Unlike']/parent::*/parent::*/parent::*")
                    if (len(unlike_button) > 0):
                        log[username].append({
                            "post": post,
                            "status": "Already liked"
                        })
                except:
                    log[username].append({
                        "post": post,
                        "status": "Error"
                    })
        self.driver.quit()
         
        with open("log.json", "w") as f:
            f.write(json.dumps(log))
            
        return log

# igg = InstagramBot()

# igg.set_login("", "")

# igg.run_login()

# igg.run_likes("imazit.lp")
