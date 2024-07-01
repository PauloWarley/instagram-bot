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
import os

class CommonsImazit():
    # print(like[0].get_attribute("outerHTML"))
    # //*[local-name() = 'svg']
    # //*[local-name() = 'svg']/ancestor::div
    # //*[local-name() = 'svg']/div::div

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
        # self.options.add_argument("--headless")
        
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
        

    def run_login(self, double_auth_callback= lambda x: x) -> bool:
        
        _uuid = uuid.uuid4()
        is_user_in_db = self.find_user_in_db(self.login)
        print(is_user_in_db)
        if (is_user_in_db != None):
            _uuid = self.find_user_in_db(self.login)
        
        self.start_webdriver(userdata = f'--user-data-dir={os.getcwd()}/userdata/{_uuid}')
        
        def is_logged() -> bool:
            if self.wait_load(".//*[local-name() ='svg' and @aria-label = 'Instagram']", self.driver, 10) == True:
                return True
            
        def is_double_auth() -> bool:
            xpath_input_code = ".//input[@aria-describedby='verificationCodeDescription']"
            if self.wait_load(xpath_input_code, self.driver, 60) == True:
                print("is_double_auth")
                double_auth_callback(self.login)
                # return True
                while True:
                    try:
                        f = open("./double_auth.json", "r")
                        codes = json.loads(f.read())
                        
                        for code in codes:
                            print(code["login"] , self.login , code["used"])
                            if code["login"] == self.login and code["used"] == False:
                                
                                print(code["code"])
                                input_code = self.driver.find_element(By.XPATH, xpath_input_code)
                                input_code.send_keys(code["code"])
                                input_code.send_keys(Keys.ENTER)
                                
                                code["used"] = True
                                break
                                
                                
                        f.close()
                        
                        f = open("./double_auth.json", "w")
                        f.write(json.dumps(codes))
                        f.close()
                        
                    except Exception as e:
                        print(e)
                        pass

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
        
        if(is_double_auth()):
            print("Situação de dupla autenticação:", True)
            
        
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

    def get_accounts(self):
        return self.df.to_dict("records")
    
igg = InstagramBot()
igg.get_accounts()

# igg.set_login("", "")

# igg.run_login()

# igg.run_likes("imazit.lp")
