import os, json
from time import perf_counter, sleep

from bs4 import BeautifulSoup

from locust import HttpUser, task, between, events, constant

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options


def get_execution_time(start_time):
    return int((perf_counter() - start_time) * 1000)


#TODO: fetch all resources
class HttpRequestLoad(HttpUser):

    fixed_count = 0

    @task
    def load_all_js_and_css(self):

        try:
        
            start_time = perf_counter()
            
            main_url = self.environment.host

            response = self.client.get(main_url, catch_response=True)

            soup = BeautifulSoup(response.content, 'html.parser')

            # selects all script tags with resources
            link_tags = soup.find_all("link")
            for tag in link_tags:
                if tag.has_attr("href") and tag['href'].endswith('.css'):
                    self.client.get(tag['href'], catch_response=True)

            # selects all script tags with resources         
            script_tags = soup.find_all("script")
            for tag in script_tags:
                if tag.has_attr("src"):
                    self.client.get(tag["src"], catch_response=True)

            load_time = get_execution_time(start_time)

            #summarizes all downloads as single request
            events.request.fire(
                request_type="GET", 
                name="load_all_js_css", 
                response_time=load_time, 
                response_length=0 #TODO
            )

        except Exception as e:

            exception_type = type(e)
            
            # Report the request duration to Locust
            events.request.fire(
                request_type="GET", 
                name="load_all_js_css", 
                response_time=0, 
                response_length=0,
                exception=exception_type
            )


class BrowserInteract(HttpUser):

    wait_time = constant(5)

    fixed_count = 2

    driver = None

    def on_start(self):
        if not self.driver:
            options = webdriver.ChromeOptions()
            # options.add_argument('--headless')
            self.driver = webdriver.Chrome(options=options)

    def on_stop(self):
        if self.driver:
            self.driver.quit()


    #TODO improve replace
    def extract_domain_from_host_url(self):
        url = self.environment.host
        url = url.replace('http:', '').replace('https:', '').replace('www.', '').replace('/', '')
        return url


    def add_cookies(self):

        domain_name = self.extract_domain_from_host_url()

        cookie_file = '{}/../data/cookies_{}.json'.format(
            os.path.dirname(os.path.abspath(__file__)),
            domain_name
        )

        print('cookie_file: ', cookie_file)

        # Load the cookies from a JSON file
        with open(cookie_file) as f:
            cookies = json.load(f)

        # Add each cookie to the Selenium session
        for cookie in cookies:
            cookie["sameSite"] = str(cookie["sameSite"])
            print('cookie: ', cookie)
            self.driver.add_cookie(cookie)


    def clear_cache(self):

        self.driver.execute_script("localStorage.clear();")
        self.driver.execute_script("sessionStorage.clear();")
        self.driver.delete_all_cookies()


    def load_login_page(self, url):

        start_time = perf_counter()

        self.driver.get(url)

        # waits for title
        WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "span.css-10trblm.e16nr0p30")
            )
        )

        self.driver.get_screenshot_as_file("./screenshot_title_presence.png")

        # gets all buttons of page with title
        logout_buttons = WebDriverWait(self.driver, 120).until(
            EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, "button")
            )
        )

        self.driver.get_screenshot_as_file("./screenshot_buttons.png")

        loaded_expected_element = False

        for button in logout_buttons:
            if button.text == 'Login':
                WebDriverWait(self.driver, 120).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "button")
                    )
                )
                loaded_expected_element = True
                break

        if not loaded_expected_element:
            raise Exception('Did not find expected element')

        return get_execution_time(start_time)
    

    def load_main_page(self, url):

        # self.driver.implicitly_wait(10)

        

        start_time = perf_counter()

        self.driver.get(url)

        self.add_cookies()

        # waits for title
        WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "span.css-10trblm.e16nr0p30")
            )
        )

        sleep(3)

        self.driver.get_screenshot_as_file("./screenshot_title_presence.png")

        loaded_expected_element = False

        for i in range(10):
            print('iteration: ', i)

            # gets all buttons of page with title
            logout_buttons = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_all_elements_located(
                    (By.CSS_SELECTOR, "button")
                )
            )

            print('buttons:\n', logout_buttons)

            self.driver.get_screenshot_as_file("./screenshot_buttons.png")

            for button in logout_buttons:
                
                try:
                    print('button: ', button.get_attribute('outerHTML'))
                    if 'Logout' in button.text:
                        WebDriverWait(self.driver, 25).until(
                            EC.element_to_be_clickable(
                                button
                            )
                        )
                        loaded_expected_element = True
                        break
                except Exception as e:
                    raise
                    print('exception: ', e)
                    pass

            if loaded_expected_element:
                break

            sleep(0.5)

        if not loaded_expected_element:
            raise Exception('Did not find expected element')

        return get_execution_time(start_time)


    @task
    def interact_on_login_page(self):

        try:

            url = self.environment.host
            
            load_time = self.load_login_page(url)

            # Report the request duration to Locust
            events.request.fire(
                request_type="GET", 
                name="load_login_page", 
                response_time=load_time, 
                response_length=0 #TODO
            )

            # TODO: collect interaction metrics

        except Exception as e:

            exception_type = type(e)
            
            # Report the request duration to Locust
            events.request.fire(
                request_type="GET", 
                name="load_login_page", 
                response_time=0, 
                response_length=0,
                exception=exception_type
            )


    @task
    def interact_on_main_page(self):

        try:

            url = self.environment.host
            
            load_time = self.load_main_page(url)
            # load_time = self.load_login_page(url)

            # Report the request duration to Locust
            events.request.fire(
                request_type="GET", 
                name="load_main_page", 
                response_time=load_time, 
                response_length=0 #TODO
            )

            # TODO: collect interaction metrics

            self.clear_cache()

        except Exception as e:
            # raise

            exception_type = type(e)
            
            # Report the request duration to Locust
            events.request.fire(
                request_type="GET", 
                name="load_main_page", 
                response_time=0, 
                response_length=0,
                exception=exception_type
            )

class APITester():
    
    @task
    def api():
        pass