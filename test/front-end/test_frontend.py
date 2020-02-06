import pytest
from flask import current_app, url_for
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import threading
import time
from config import TestConfig
from app import create_app



def login(driver):
    driver.get(url_for('auth.welcome', _external=True))
    username = driver.find_element_by_id("username")
    username.send_keys("jjones")
    password = driver.find_element_by_id("password")
    password.send_keys("password")
    submit = driver.find_element_by_id("submit")
    submit.click()

@pytest.fixture(scope="class")
def driver(server):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    login(driver)
    yield driver
    driver.get(url_for('auth.server_shutdown', _external=True))
    driver.quit()

@pytest.fixture(scope="class")
def server(app):
    server_thread = threading.Thread(target=app.run, kwargs={'debug':False, 'port': 5000, 'use_reloader': False, 'threaded': True})
    server_thread.start()
    time.sleep(1)
    yield server_thread
    print(server_thread)
    server_thread.join()

def start_app(*args, **kwargs):
    app = create_app(TestConfig)
    app.run(**kwargs)  

class TestWelcome(object):

    def test_login(self, server, driver, dbSession):
        url = url_for('auth.welcome', _external=True)
        print(url)
        driver.get(url)
        print(driver.title)
        assert "Ask Your Peeps" in driver.page_source

@pytest.mark.usefixtures("dbSession")
class TestIndex(object):

    def get_url(self):
        url = url_for('main.index', _external=True)
        return url

    def test_manual_location_toggle(self, driver):
        driver.get(self.get_url())
        manual = driver.find_element_by_id("manual_location")
        assert manual.is_displayed() == False
        location_select = Select(driver.find_element_by_id("location"))
        location_select.select_by_value("manual")
        assert manual.is_displayed() == True

    def test_category(self, driver):
        driver.get(self.get_url())
        category = Select(driver.find_element_by_id("category"))
        options = list(map(lambda x: x.text, category.options))
        assert "Electrician" in options
        assert "Mexican Restaurant" not in options

        sector = Select(driver.find_element_by_id("sector"))
        sector.select_by_index(1)
        category = Select(driver.find_element_by_id("category"))
        options = list(map(lambda x: x.text, category.options))
        assert "Electrician" not in options
        assert "Mexican Restaurant" in options

    def test_gps_location(self, driver):
        driver.get(self.get_url())
        driver.execute_script("window.navigator.geolocation.getCurrentPosition = function(success){ var position = {'coords' : {'latitude': 555, 'longitude': 999},}; success(position); }")
        gpsLat = driver.find_element_by_id("gpsLat")
        gpsLong = driver.find_element_by_id("gpsLong")
        assert gpsLat.get_attribute("value") == ""
        assert gpsLong.get_attribute("value") == ""
        location_select = Select(driver.find_element_by_id("location"))
        location_select.select_by_value("gps")
        assert gpsLat.get_attribute("value") == '555'
        assert gpsLong.get_attribute("value") == '999'

    def test_map_toggle(self, driver):
        driver.get(self.get_url())
        category = Select(driver.find_element_by_id("category"))
        category.select_by_index(0)
        submit = driver.find_element_by_id("submit")
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()
        list_items = driver.find_element_by_id("list_items")
        assert list_items.is_displayed()
        showMap = driver.find_element_by_id("viewOnMap")
        driver.execute_script("arguments[0].scrollIntoView();", showMap)
        showMap.click()
        assert not list_items.is_displayed()
        showList = driver.find_element_by_id("viewList")
        showList.click()
        assert list_items.is_displayed()

    def test_autocomplete(self, driver):
        driver.get(self.get_url())
        provider = driver.find_element_by_id("name_typeahead")
        input = provider.find_element_by_tag_name("input")
        input.send_keys("Ev")
        autocomplete = driver.find_elements_by_class_name("vbst-item")
        target = list(filter(lambda x: x.text=="Evers Electric", autocomplete))
        assert target != []
        target[0].click()
        name = driver.find_element_by_id("provider_name")
        assert name.get_attribute("value") == "Evers Electric"
        assert input.get_attribute("value") == "Evers Electric"