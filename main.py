from bs4 import BeautifulSoup
from selenium import webdriver
import time, os, json

email = 'enter email here'
password = 'enter password here'
#door id can be found in the page source of the myq dashboard
door_id = 'enter door id here'

time_log = os.path.dirname(os.path.realpath(__file__))+'/time_log.json'

class timer():
    def __init__(self, time_log, buffer = 61):
        self.__time_log = time_log
        self.__buffer = buffer
    def __past_time(self):
        try:
            with open(self.__time_log) as data_file:
                log_time = json.load(data_file)
            with open(self.__time_log, 'w') as f:
                json.dump(time.time(), f, sort_keys=True, indent=4, ensure_ascii=False)
            return float(log_time)
        except:
            with open(self.__time_log, 'w') as f:
                json.dump(time.time(), f, sort_keys=True, indent=4, ensure_ascii=False)
            return float(0)
    def __current_time(self):
        return time.time()
    def test_time(self):
        return self.__current_time() - self.__past_time() >= self.__buffer
class myqdoor():
    def __init__(self, username, password, door_id, time_log):
        self.__username = username
        self.__password = password
        self.__door_id = door_id
        self.__time_log = time_log
        self.__websession = -1
        self.__driver = -1
        self.__start()
    def __start(self):
        self.__websession = myqdoor_websession(self.__username, self.__password, self.__time_log)
        self.__driver = self.__websession.start()
    def open(self):
        if self.__driver != -1:
            if doorStatus(self.__driver.page_source.encode('ascii','ignore'), self.__door_id):
                door_driver = self.__driver.find_element_by_id(self.__door_id)
                door_driver.find_element_by_class_name("device-img").click()
    def close(self):
        if self.__driver != -1:
            if not doorStatus(self.__driver.page_source.encode('ascii','ignore'), self.__door_id):
                door_driver = self.__driver.find_element_by_id(self.__door_id)
                door_driver.find_element_by_class_name("device-img").click()
class myqdoor_websession():
    def __init__(self, username, password, time_log):
        self.__username = username
        self.__password = password
        self.__time_log = time_log
    def start(self):
        test_time = timer(self.__time_log)
        if test_time.test_time():
            return self.__login()
        else:
            return -1
    def __login(self):
        driver = webdriver.PhantomJS()
        driver.set_window_size(1120, 550)
        driver.get("https://www.mychamberlain.com/")
        driver.find_element_by_name("Email").send_keys(self.__username)
        driver.find_element_by_name("Password").send_keys(self.__password)
        driver.find_element_by_class_name("js-login-submit").click()
        if 'Dashboard' not in driver.title:
            print("Error: Login failure.")
            exit()
        else:
            return driver
def doorSource(webpage_source, door_id):
    soup = BeautifulSoup(webpage_source, "html5lib")
    return soup.find("div", {"id": door_id})
def doorStatus(source, door_id):
    door = doorSource(source, door_id)
    status = door.find("div", {"class":"device-status"})
    return status.find("span", {"data-bind":"text: devicestate"}).string == "Closed"
door = myqdoor(email, password, door_id, time_log)
door.open()
