import pytest
from flask import current_app, url_for
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
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
    # options.add_argument('--enable-logging')
    # options.add_argument('--logging-level=0')
    # capabilities = DesiredCapabilities.CHROME.copy()
    # capabilities['loggingPrefs'] = {'browser': 'ALL'}
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    login(driver)
    yield driver
    time.sleep(2)
    driver.quit()

@pytest.fixture(scope="class")
def server(app):
    server_thread = threading.Thread(target=app.run, kwargs={'debug':False, 'port': 5000, 'use_reloader': False, 'threaded': True})
    server_thread.start()
    time.sleep(1)
    yield server_thread
    server_thread.join()

def start_app(*args, **kwargs):
    app = create_app(TestConfig)
    app.run(**kwargs)  

def wait_for_page_load(driver, timeout=1):
    is_not_done_loading = True
    while is_not_done_loading:
        before = driver.page_source
        time.sleep(timeout)
        after = driver.page_source
        is_not_done_loading = (before != after)


class TestWelcome(object):

    def test_login(self, driver, dbSession, server):
        driver.execute_script("console.log('test')")
        url = url_for('auth.welcome', _external=True)
        driver.get(url)
        assert "Ask Your Peeps" in driver.page_source
        wait_for_page_load(driver)


@pytest.mark.usefixtures("dbSession")
class TestIndex(object):

    def get_url(self):
        url = url_for('main.index', _external=True)
        return url

    def test_manual_location_toggle(self, driver):
        driver.get(self.get_url())
        manual = WebDriverWait(driver, 10)\
                    .until(EC.presence_of_element_located(
                        (By.ID, 'manual_location')))
        assert manual.is_displayed() == False
        location_select = Select(driver.find_element_by_id("location"))
        location_select.select_by_value("manual")
        assert manual.is_displayed() == True

    def test_category_get(self, driver):
        driver.get(self.get_url())
        sector = Select(driver.find_element_by_id('search_sector'))
        sector.select_by_value('1')
        category = Select(driver.find_element_by_id("search_category"))
        wait_for_page_load(driver)
        options = list(map(lambda x: x.text, category.options))
        assert "Electrician" in options
        assert "Mexican Restaurant" not in options

        sector = Select(driver.find_element_by_id("search_sector"))
        sector.select_by_value('2')
        category = Select(driver.find_element_by_id("search_category"))
        wait_for_page_load(driver)
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
        wait_for_page_load(driver)
        assert gpsLat.get_attribute("value") == '555'
        assert gpsLong.get_attribute("value") == '999'

    def test_map_toggle(self, driver):
        driver.get(self.get_url())
        sector = Select(driver.find_element_by_id("search_sector"))
        sector.select_by_value("1")        
        category = Select(driver.find_element_by_id("search_category"))
        category.select_by_value("1")
        submit = driver.find_element_by_id("submit")
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()
        wait_for_page_load(driver)
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
        sector = Select(driver.find_element_by_id("search_sector"))
        sector.select_by_value("1")
        category = Select(WebDriverWait(driver, 10)\
                    .until(EC.presence_of_element_located(
                        (By.ID, 'search_category'))))
        category.select_by_visible_text("Electrician")
        provider = driver.find_element_by_id("name_typeahead")
        input = provider.find_element_by_tag_name("input")
        driver.execute_script("arguments[0].scrollIntoView();", input)
        input.send_keys("Ev")
        wait_for_page_load(driver)
        autocomplete = driver.find_elements_by_class_name("vbst-item")
        target = list(filter(lambda x: x.text=="Evers Electric", autocomplete))
        assert target != []
        target[0].click()
        wait_for_page_load(driver)
        name = driver.find_element_by_id("provider_name")
        assert name.get_attribute("value") == "Evers Electric"
        assert input.get_attribute("value") == "Evers Electric"

    def test_send_correction(self, driver):
        driver.get(self.get_url())
        sector_el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'search_sector')))
        sector = Select(sector_el)
        sector.select_by_value("1")        
        wait_for_page_load(driver)
        category = Select(driver.find_element_by_id("search_category"))
        category.select_by_value("1")
        submit = driver.find_element_by_id("submit")
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()
        modal_links = WebDriverWait(driver, 10)\
                        .until(EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR,
                            'button[data-target="#suggestion-modal"]')))
        assert len(modal_links) > 0
        toClick = modal_links[0]
        driver.execute_script("arguments[0].scrollIntoView();", toClick)
        toClick.click()
        modal = WebDriverWait(driver, 10)\
                .until(EC.visibility_of_element_located(
                    (By.ID, 'suggestion-modal')))
        assert modal.is_displayed()
        is_not_active = modal.find_element_by_id('is_not_active')
        driver.execute_script("arguments[0].scrollIntoView();", is_not_active)
        is_not_active.click()
        submit = modal.find_elements_by_css_selector('button[type="submit"]')[0]
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == 'Message sent'
        alert.accept()

    def test_send_correction_address(self, driver):
        driver.get(self.get_url())
        sector_el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'search_sector')))
        sector = Select(sector_el)
        sector.select_by_value("1")        
        wait_for_page_load(driver)
        category = Select(driver.find_element_by_id("search_category"))
        category.select_by_value("1")
        submit = driver.find_element_by_id("submit")
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()
        modal_links = WebDriverWait(driver, 10)\
                        .until(EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR,
                            'button[data-target="#suggestion-modal"]')))
        assert len(modal_links) > 0
        toClick = modal_links[0]
        driver.execute_script("arguments[0].scrollIntoView();", toClick)
        toClick.click()
        modal = WebDriverWait(driver, 10)\
                .until(EC.visibility_of_element_located(
                    (By.ID, 'suggestion-modal')))
        assert modal.is_displayed()
        address_updated = modal.find_element_by_id('address_updated')
        driver.execute_script("arguments[0].scrollIntoView();", address_updated)
        address_updated.click()
        submit = modal.find_elements_by_css_selector('button[type="submit"]')[0]
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert alert.text == 'Message sent'
        alert.accept()


