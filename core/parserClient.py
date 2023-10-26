from selenium import webdriver
from selenium.webdriver.common.by import By

from core.localStorage import LocalStorage
import time, json, os


class Client:
    def __init__(self) -> None:
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.result = {}


    def init_localStorage(self):
        self.driver.get("https://web.telegram.org/a/")

        self.driver.implicitly_wait(5)
        storage = LocalStorage(self.driver)
        with open("data/localStorage.json", "r+") as f:
            r = json.loads(f.read())
            for k in r:
                storage.set(k, r[k])
        self.driver.refresh()
        self.driver.implicitly_wait(3)


    def get_localStorage(self):
        self.driver.get("https://web.telegram.org/a/")

        self.driver.implicitly_wait(5)

        time.sleep(60)
        storage = LocalStorage(self.driver)
        storage["tt-global-state"] = ""

        print(storage)
        with open("data/localStorage_update.json", "w+") as f:

            f.write(json.loads(storage))


    def findPostByWordInChannels(self):
        with open("data/channels.json") as f:
            data = json.loads(f.read())
            for channel in data["channels"]:
                try:
                    channelName = str(channel).split("/")[-1]
                    inpSearch = self.driver.find_element(
                        By.ID,
                        "telegram-search-input"
                    )
                    inpSearch.clear()
                    inpSearch.send_keys(channelName)
                    
                    self.driver.implicitly_wait(5)
                    time.sleep(1.5)

                    self.driver.find_element(
                        By.CLASS_NAME,
                        "search-result"
                    ).find_element(
                        By.CLASS_NAME,
                        "ListItem-button"
                    ).click()

                    self.driver.implicitly_wait(45)
                    time.sleep(1.5)

                    self.driver.find_element(
                        By.XPATH,
                        '//button[@aria-label="Search this chat"]'
                    ).click()

                    self.driver.implicitly_wait(45)
                    time.sleep(0.5)
                    self.result[channelName] = {}

                    for word in data["content"][channel]:
                        inpSearch = self.driver.find_element(
                            By.XPATH,
                            "/html/body/div[2]/div/div[3]/div/div[1]/div/div/div/input"
                        )
                        inpSearch.clear()
                        inpSearch.send_keys(word)

                        self.driver.implicitly_wait(45)
                        time.sleep(2)
                        result = []

                        if self.driver.find_element(
                            By.CLASS_NAME,
                            "helper-text"
                        ).text == "No messages found":
                            continue

                        for k in self.driver.find_elements(
                            By.CLASS_NAME,
                            "search-result-message"
                        ):
                            k.find_element(
                                By.CLASS_NAME,
                                "ListItem-button"
                            ).click()

                            self.driver.implicitly_wait(45)
                            time.sleep(2)

                            for j in self.driver.find_elements(
                                By.CLASS_NAME,
                                "Message"
                            ):
                                if str(word).lower() in j.text.lower():
                                    result.append(channel + "/" + j.get_attribute("id").split("message")[-1])
                        self.result[channelName][word] = result
                except:
                    pass


    def run(self, user_id):
        self.init_localStorage()
        self.findPostByWordInChannels()

        pathFile: str = f"users/channelMessages_{user_id}.json"

        self.save_file(pathFile)
        print(f"[+] The result is found along this path: {os.path.abspath(pathFile)}")
    

    def save_file(self, path):
        with open(path, "w+") as file:
            file.write(
                json.dumps(self.result, indent=4)
            )