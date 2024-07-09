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

from MongoDB import MongoDB

class CommonsImazit():
    def wait_load(self, xpath, driver, timeout = 5*60):
        loaded = False
        last_time = time.time()
        print("Aguardando carregar elemento", xpath)
        
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
            if (verify_time):
                print("time case")
                return False
        
        print("Elemento carregado.")
        return loaded

class InstagramBot():
    
    def __init__(self):
        cm = CommonsImazit()
        
        mongo_uri = "mongodb+srv://fanzo-manager-prod:zSCiM6QtpBMZmD8t@prod-fanzo.s5pj0hj.mongodb.net/social-media-service?retryWrites=true&w=majority"
        
        self.wait_load = cm.wait_load
        self.url= "https://www.instagram.com"
        # BANCO DE DADOS
        self.mongo = MongoDB()

        # Conectar ao MongoDB
        client = self.mongo.connect_to_mongodb(mongo_uri)
        self.db = client.get_database()
    
        self.options = webdriver.ChromeOptions()

        # options.add_experimental_option('--excludeSwitches', ['disable-logging'])
        self.options.add_argument('--log-level=3')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument('--ignore-certificate-errors-spki-list')
        self.options.add_argument("--start-maximized")
        
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--remote-debugging-port=9222')
        self.options.add_argument('--window-size=1920,1080')  # Emular resolução de tela
        self.options.add_argument('--disable-software-rasterizer')  # Habilitar renderização de GPU

        
    def start_webdriver(self, cookies):
        service = Service(ChromeDriverManager().install())
        
        # self.options.add_argument("--window-position=2000,0")
        # self.options.add_argument("--window-size=1920,1080")
        # self.options.add_argument("--headless")
        
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
        is_user_in_db = self.find_user_in_db(self.login)
        if (is_user_in_db != None):
            user = self.find_user_in_db(self.login)
            cookies = user["social_media"]["instagram"]["credentials"]["cookies"]
            try:
                cookies = json.loads(cookies)
            except:
                cookies = []
        else:
            return False
        
        self.start_webdriver(cookies=cookies)
        
        def is_logged() -> bool:
            if self.wait_load(".//*[local-name() ='svg' and @aria-label = 'Instagram']", self.driver, 10) == True:
                return True
            
        def is_double_auth() -> bool:
            xpath_input_code = ".//input[@aria-describedby='verificationCodeDescription']"
            if self.wait_load(xpath_input_code, self.driver, 60) == True:
                print("is_double_auth")
                
                code_description_xpath = ".//div[@id='verificationCodeDescription']"
                
                self.wait_load(xpath_input_code, self.driver, 60) 
                code_description = self.driver.find_element(By.XPATH, code_description_xpath).text
                
                print("code_description", code_description)
                
                double_auth_callback(self.login, code_description)
                # return True
                
                print("Aguardando código de autenticação para:", self.login)
                
                while True:
                    try:
                        used = True
                        
                        timeout = 60
                        
                        while used:
                            print("Aguardando o código por 1 minutos. Usuário:", self.login)
                            user = self.find_user_in_db(self.login)
                            code = user["social_media"]["instagram"]["credentials"]["code"]
                            
                            used = code["used"]
                            
                            if (timeout >= 0):
                                timeout = timeout - 1
                                time.sleep(1)
                            else:
                                print("Código de dupla auth não inserido para o usuário:", self.login)
                                return self.driver.quit()
                            
                        input_code = self.driver.find_element(By.XPATH, xpath_input_code)
                        input_code.send_keys(code["code"])
                        input_code.send_keys(Keys.ENTER)
                        
                        self.save_user_in_db(login=self.login, code=code["code"], code_used=True)
                        
                        return True
                        
                    except Exception as e:
                        print(e)
                        pass


        self.driver.get(self.url)
        
        self.driver.save_screenshot("./screenshot.png")
        
        
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
        
        self.save_user_in_db(login=self.login, cookies=self.driver.get_cookies())
        
        return self.driver.quit()
    
    def find_user_in_db(self, login):
        document = self.mongo.find_document_by_username(self.db, "social", login)
        if (document):
            return document
        else:
            return None
    
    def save_user_in_db(self, login, code = None, code_used = False, cookies = None):
        document = self.mongo.find_document_by_username(self.db, "social", login)

        if document:
            print("Documento encontrado antes da atualização:")
            # print(document)
            
            # Atualização do documento
            update_query = {"_id": document["_id"]}  # Supondo que você queira atualizar pelo ID
            
            if ( cookies != None ):
                cookies = json.dumps(cookies)
                
                update_data = {"social_media.instagram.credentials.cookies": cookies}
                update_result = self.mongo.update_document(self.db, "social", update_query, update_data)
                
                if update_result.modified_count > 0:
                    print(f"Documento atualizado com sucesso. Novo valor para 'cookie'.")
                else:
                    print("Nenhum documento foi atualizado.")
            
            if ( code != None ):
                new_code = {
                    "code": code,
                    "used": code_used
                }
                
                update_data = {"social_media.instagram.credentials.code": new_code}
                update_result = self.mongo.update_document(self.db, "social", update_query, update_data)

                if update_result.modified_count > 0:
                    print(f"Documento atualizado com sucesso. Novo valor para 'code'.")
                else:
                    print("Nenhum documento foi atualizado.")
    
    def run_likes(self, login: str,  username: str):
        is_user_in_db = self.find_user_in_db(login)
        if (is_user_in_db != None):
            user = self.find_user_in_db(login)
            cookies = user["social_media"]["instagram"]["credentials"]["cookies"]
            try:
                cookies = json.loads(cookies)
            except:
                cookies = []
                
            self.start_webdriver(cookies=cookies)
        else:
            return {
                "status": "User are not authenticated."
            }
        
        self.driver.get(f"{self.url}/{username}")
        
        for cookie in cookies:
            # print(cookie)
            self.driver.add_cookie(cookie)
            
        print(f"{self.url}/{username}")
        self.driver.get(f"{self.url}/{username}")
        
        self.driver.save_screenshot("./screenshot.png")
        

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
            self.driver.save_screenshot("./screenshot.png")
            
            print("Aguardando para dar like na foto.", post)
            self.wait_load(".//section/div//*[@role='button']//*[local-name() = 'svg' and @aria-label='Like']", self.driver,)
            try:
                time.sleep(5)
                like_button = self.driver.find_element(By.XPATH, ".//section/div//*[@role='button']//*[local-name() = 'svg' and @aria-label='Like']")
                self.actions.move_to_element(like_button).perform()
                like_button = self.driver.find_element(By.XPATH, ".//section/div//*[@role='button']//*[local-name() = 'svg' and @aria-label='Like']")
                like_button.click()
                self.wait_load(".//section/div//*[@role='button']//*[local-name() = 'svg' and @aria-label='Unlike']", self.driver)
                
                log[username].append({
                    "post": post,
                    "status": "Liked"
                })
                
                time.sleep(5)
                
            except Exception as e:
                try:
                    unlike_button = self.driver.find_element(By.XPATH, ".//section/div//*[@role='button']//*[local-name() = 'svg' and @aria-label='Unlike']")
                    if (len(unlike_button) > 0):
                        log[username].append({
                            "post": post,
                            "status": "Already liked"
                        })
                except Exception as e:
                    log[username].append({
                        "post": post,
                        "status": "Error"
                    })
        self.driver.quit()
         
        with open("log.json", "w") as f:
            f.write(json.dumps(log))
            
        return log

    # def get_accounts(self):
    #     document = self.mongo.find_all_documents( self.db, "social")
    #     if (document):
    #         accounts = []
    #         for doc in document:
    #             accounts.append(doc["social_media"]["instagram"]["credentials"]["user_name"])
            
    #         return accounts
    #     else:
    #         return None
