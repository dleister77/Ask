import pytest
from flask import url_for
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
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


@pytest.fixture(scope="function")
def driver(server, request):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    if getattr(request.cls, 'logged_in'):
        login(driver)
        wait_for_page_load(driver, 2)
    url = getattr(request.cls, 'url')
    if url:
        params = getattr(request.cls, 'url_params', {})
        full_url = url_for(url, _external=True, **params)
        driver.get(full_url)
        wait_for_page_load(driver, 2)
    yield driver
    time.sleep(1)
    shutdown_url = url_for('auth.server_shutdown', _external=True)
    driver.get(shutdown_url)
    driver.quit()


@pytest.fixture(scope="function")
def server(app, dbSession):
    app_kwargs = {
        'debug': False, 'port': 5000, 'use_reloader': False, 'threaded': True
    }
    server_thread = threading.Thread(target=app.run, kwargs=app_kwargs)
    server_thread.start()
    time.sleep(1)
    yield server_thread
    server_thread.join()


def start_app(*args, **kwargs):
    app = create_app(TestConfig)
    app.run(**kwargs)


def wait_for_page_load(driver, timeout=2):
    is_not_done_loading = True
    while is_not_done_loading:
        before = driver.page_source
        time.sleep(timeout)
        after = driver.page_source
        is_not_done_loading = (before != after)


class TestWelcome(object):

    logged_in = False
    url = 'auth.welcome'

    def test_login(self, driver, dbSession):
        driver.execute_script("console.log('test')")
        url = url_for('auth.welcome', _external=True)
        driver.get(url)
        assert "Ask Your Peeps" in driver.page_source
        wait_for_page_load(driver)


@pytest.mark.usefixtures("dbSession")
class TestIndex(object):

    logged_in = True
    url = 'main.index'

    def get_url(self):
        url = url_for('main.index', _external=True)
        return url

    def test_manual_location_toggle(self, driver):
        manual = WebDriverWait(driver, 10)\
            .until(EC.presence_of_element_located((By.ID, 'manual_location')))
        assert manual.is_displayed() is False
        location_select = Select(driver.find_element_by_id("location"))
        location_select.select_by_value("manual")
        assert manual.is_displayed() is True

    def test_category_get(self, driver):
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
        target = list(
            filter(lambda x: x.text == "Evers Electric", autocomplete)
        )
        assert target != []
        target[0].click()
        wait_for_page_load(driver)
        name = driver.find_element_by_id("provider_name")
        assert name.get_attribute("value") == "Evers Electric"
        assert input.get_attribute("value") == "Evers Electric"

    def test_send_correction(self, driver):
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
                            'a[data-target="#suggestion-modal"]')))
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
        submit = modal.find_element_by_id('suggestion_form_submit')
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()
        alert = driver.find_element_by_id("swal2-title")
        assert alert.text == 'Message sent'

    def test_send_correction_address(self, driver):
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
                            'a[data-target="#suggestion-modal"]')))
        assert len(modal_links) > 0, "no modal links"
        toClick = modal_links[0]
        driver.execute_script("arguments[0].scrollIntoView();", toClick)
        toClick.click()
        modal = WebDriverWait(driver, 10)\
                .until(EC.visibility_of_element_located(
                    (By.ID, 'suggestion-modal')))
        assert modal.is_displayed(), "modal not displayed"
        address_updated = modal.find_element_by_id('address_updated')
        driver.execute_script(
            "arguments[0].scrollIntoView();", address_updated
        )
        address_updated.click()
        city = modal.find_element_by_id('city')
        city.send_keys("San Diego")
        submit = modal.find_element_by_id('suggestion_form_submit')
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()
        alert = driver.find_element_by_id("swal2-title")
        assert alert.text == 'Message sent'


class TestRegister(object):

    logged_in = False
    url = 'auth.register'

    def complete_form(self, driver):
        first_name = driver.find_element_by_id('first_name')
        first_name.send_keys('Conan')
        last_name = driver.find_element_by_id('last_name')
        last_name.send_keys('TheBarbarian')
        line1 = driver.find_element_by_id('address-line1')
        line1.send_keys('7708 Covey Chase Dr')
        city = driver.find_element_by_id('address-city')
        city.send_keys('Charlotte')
        state = driver.find_element_by_id('address-state')
        state_select = Select(state)
        state_select.select_by_value("1")
        zip = driver.find_element_by_id('address-zip')
        zip.send_keys('28210')
        email = driver.find_element_by_id('email')
        email.send_keys('conan@barbarians.com')
        username = driver.find_element_by_id('username')
        username.send_keys('conan')
        password = driver.find_element_by_id('password')
        password.send_keys('password12')
        confirmation = driver.find_element_by_id('confirmation')
        confirmation.send_keys('password12')

    def test_valid(self, driver):
        self.complete_form(driver)
        submit = driver.find_element_by_id('submit')
        submit.click()
        flash = "Congratulations! You've successfully registered."
        assert flash in driver.page_source

    def test_invalid(self, driver):
        self.complete_form(driver)
        driver.find_element_by_id('first_name').clear()
        submit = driver.find_element_by_id('submit')
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()
        error_message = driver.find_element_by_id("swal2-title")
        msg = 'Unable to Send Message'
        assert error_message.text == msg, "invalid form not caught in browser"
        error = "First Name is required."
        assert error in driver.page_source

    def test_invalid_sse(self, driver):
        self.complete_form(driver)
        email = driver.find_element_by_id('email')
        email.clear()
        email.send_keys("jjones@yahoo.com")
        submit = driver.find_element_by_id('submit')
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()
        error = 'Email address is already registered.'
        print(driver.page_source)
        assert error in driver.page_source


class TestUserProfile(object):
    logged_in = True
    url = 'main.user'
    url_params = dict(username='sarahsmith')

    def test_send_msg_via_profile(self, driver):
        profile = driver.find_element_by_id('user_profile')
        message_link = profile.find_element_by_tag_name('a')
        message_link.click()
        modal = driver.find_element_by_id('message-modal')
        subject = modal.find_element_by_id('subject')
        subject.send_keys('test subject')
        body = modal.find_element_by_id('body')
        body.send_keys('this is a test message')
        submit = modal.find_element_by_id('usermessage_form_submit')
        submit.click()
        alert_message = driver.find_element_by_id("swal2-title").text
        success_msg = "Message sent"
        assert alert_message == success_msg,\
            "message not sent when it should have been"
        alert_button = driver.find_element_by_css_selector('button.swal2-confirm')
        alert_button.click()

    def test_modal_send_invalid(self, driver):
        profile = driver.find_element_by_id('user_profile')
        message_link = profile.find_element_by_tag_name('a')
        message_link.click()
        modal = driver.find_element_by_id('message-modal')
        body = modal.find_element_by_id('body')
        body.send_keys('this is a test message')
        submit = modal.find_element_by_id('usermessage_form_submit')
        submit.click()
        alert_message = driver.find_element_by_id("swal2-title").text
        failure_msg = "Unable to Send Message"
        assert alert_message == failure_msg,\
            "message sent when it should not have been"

    def test_send_msg_via_review(self, driver):
        reviews = driver.find_element_by_id('reviews')
        review = reviews.find_elements_by_class_name('card')[0]
        message_link = review.find_element_by_css_selector('a[data-target="#message-modal"]')
        driver.execute_script("arguments[0].scrollIntoView();", message_link)
        message_link.click()
        modal = driver.find_element_by_id('message-modal')
        recipient = modal.find_element_by_id('recipient')
        assert recipient.get_attribute('value') == 'Sarah Smith',\
            'recipient not populating correctly'
        subject = modal.find_element_by_id('subject')
        assert subject.get_attribute('value') == 'Douthit Electrical',\
            'msg subject not properly updated'
        body = modal.find_element_by_id('body')
        body.send_keys('this is a test message')
        submit = modal.find_element_by_id('usermessage_form_submit')
        submit.click()
        alert_message = driver.find_element_by_id("swal2-title").text
        success_msg = "Message sent"
        failure_msg = "Please correct errors and resubmit"
        assert alert_message == success_msg,\
            "message not sent when it should have been"
        assert alert_message != failure_msg
        alert_button = driver.find_element_by_css_selector('button.swal2-confirm')
        alert_button.click()


class TestProvideProfile(object):
    logged_in = True
    url = 'main.provider'
    url_params = dict(name='Douthit Electrical', id=1)

    def test_send_reviewer_message(self, driver):
        reviews = driver.find_element_by_id("reviews")
        review = reviews.find_elements_by_class_name('card')[1]
        message_link = review.find_element_by_css_selector('a[data-target="#message-modal"]')
        driver.execute_script("arguments[0].scrollIntoView();", message_link)
        message_link.click()
        modal = driver.find_element_by_id('message-modal')
        recipient = modal.find_element_by_id('recipient')
        print(recipient.get_attribute('value'))
        assert recipient.get_attribute('value') == 'Mark Johnson',\
            'recipient not populating correctly'
        subject = modal.find_element_by_id('subject')
        assert subject.get_attribute('value') == 'Douthit Electrical',\
            'msg subject not properly updated'
        body = modal.find_element_by_id('body')
        body.send_keys('this is a test message')
        submit = modal.find_element_by_id('usermessage_form_submit')
        submit.click()
        alert_message = driver.find_element_by_id("swal2-title").text
        success_msg = "Message sent"
        failure_msg = "Please correct errors and resubmit"
        assert alert_message == success_msg,\
            "message not sent when it should have been"
        assert alert_message != failure_msg
        alert_button = driver.find_element_by_css_selector('button.swal2-confirm')
        alert_button.click()


class TestMessages(object):

    logged_in = True
    url = 'main.view_messages'
    url_params = dict(folder='inbox')

    def test_inbox_read_reply(self, driver):
        inbox = driver.find_element_by_id('folder')
        rows = inbox.find_elements_by_tag_name('tr')
        num_rows = len(rows) - 1  # subtracts out header
        assert num_rows == 2
        row_1 = rows[1]
        assert 'Sarah Smith' in row_1.text
        row_1.click()
        message = driver.find_element_by_id('message-read')
        header = message.find_element_by_id('message-read-header')
        header_elements = header.find_elements_by_class_name('message-read')
        assert header_elements[0].text == 'Sarah Smith'
        assert header_elements[1].text == 'yet another test subject'
        body = message.find_element_by_id('message-read-body')
        assert body.text == " yet another test body"
        next = driver.find_element_by_id('next-message')
        next.click()
        header = message.find_element_by_id('message-read-header')
        header_elements = header.find_elements_by_class_name('message-read')
        assert header_elements[1].text == 'test subject'
        previous = driver.find_element_by_id("previous-message")
        previous.click()
        header = message.find_element_by_id('message-read-header')
        header_elements = header.find_elements_by_class_name('message-read')
        assert header_elements[1].text == 'yet another test subject'
        reply = driver.find_element_by_id("reply-to")
        reply.click()
        recipient = driver.find_element_by_id("recipient")
        assert recipient.get_attribute('value') == "Sarah Smith"
        subject = driver.find_element_by_id("subject")
        assert subject.get_attribute('value') == "Re: yet another test subject"
        submit = driver.find_element_by_id("message-form-submit")
        driver.execute_script("arguments[0].scrollIntoView();", submit)
        submit.click()
        alert_message = driver.find_element_by_id("swal2-title").text
        success_msg = "Message Sent"
        assert alert_message == success_msg,\
            "message not sent when it should have been"

    def test_send_new(self, driver):
        new_message = driver.find_element_by_id('new-message')
        new_message.click()
        subject = driver.find_element_by_id("subject")
        subject.send_keys("the weather")
        body = driver.find_element_by_id("body")
        body.send_keys("its raining")
        typeahead = driver.find_element_by_id("recipient_typeahead")
        input = typeahead.find_element_by_tag_name('input')
        input.send_keys("Sara")
        autocomplete = driver.find_elements_by_class_name("vbst-item")
        dropdown = list(
            filter(lambda x: x.text == "Sarah Smith", autocomplete)
        )
        assert dropdown != []
        dropdown[0].click()
        assert input.get_attribute('value') == 'Sarah Smith'
        submit = driver.find_element_by_id('message-form-submit')
        submit.click()
        alert_message = driver.find_element_by_id("swal2-title").text
        success_msg = "Message Sent"
        assert alert_message == success_msg,\
            "message not sent when it should have been"

