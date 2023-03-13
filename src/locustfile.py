import os, json
from time import perf_counter, sleep
from dotenv import load_dotenv
import urllib.parse

from bs4 import BeautifulSoup

from locust import HttpUser, task, between, constant, events
from locust.stats import RequestStats

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from post_process import manage_post_processing


load_dotenv()

@events.quitting.add_listener
def extend_report(environment, **kwargs):
    manage_post_processing()


# @events.test_stop.add_listener
# def on_test_stop(environment, **kwargs):
#     # Print out the stats_history dictionary
#     print(type(environment.runner.stats))
#     print('entries: \n', environment.runner.stats.entries)
#     print('history: \n', environment.runner.stats.history)
#     print('use_response_times_cache: \n', environment.runner.stats.use_response_times_cache)
#     entries = str(environment.runner.stats.entries)


def get_execution_time(start_time):
    return int((perf_counter() - start_time) * 1000)


def url_from_domain(domain):
    return 'https://www.{}'.format(domain)


#TODO: fetch all resources
# class HttpRequestLoader(HttpUser):

#     wait_time = between(1,5)

#     fixed_count = 4


#     def load_all_resources(self, main_url, stage):

#         try:
        
#             start_time = perf_counter()

#             response = self.client.get(main_url, catch_response=True)

#             soup = BeautifulSoup(response.content, 'html.parser')

#             # selects all script tags with resources
#             link_tags = soup.find_all("link")
#             for tag in link_tags:
#                 if tag.has_attr("href") and tag['href'].endswith('.css'):
#                     self.client.get(tag['href'], catch_response=True)

#             # selects all script tags with resources         
#             script_tags = soup.find_all("script")
#             for tag in script_tags:
#                 if tag.has_attr("src"):
#                     self.client.get(tag["src"], catch_response=True)

#             load_time = get_execution_time(start_time)

#             #summarizes all downloads as single request
#             events.request.fire(
#                 request_type="GET", 
#                 name=f"{stage}_load_all_resources", 
#                 response_time=load_time, 
#                 response_length=0 #TODO
#             )

#         except Exception as e:
            
#             exception_type = type(e)
            
#             # Report the request duration to Locust
#             events.request.fire(
#                 request_type="GET", 
#                 name=f"{stage}_load_all_resources", 
#                 response_time=0, 
#                 response_length=0,
#                 exception=exception_type
#             )

    
#     @task
#     def dev_load_all_resources(self):
#         url = url_from_domain(os.getenv("DOMAIN_DEV"))
#         self.load_all_resources(url, 'dev')

    
#     @task
#     def prod_load_all_resources(self):
#         url = url_from_domain(os.getenv("DOMAIN_PROD"))
#         self.load_all_resources(url, 'prod')


# class BrowserInteractor(HttpUser):

#     wait_time = between(1,5)

#     fixed_count = 2

#     driver = None

#     def on_start(self):
#         if not self.driver:
#             options = webdriver.ChromeOptions()
#             # options.add_argument('--headless')
#             self.driver = webdriver.Chrome(options=options)


#     def on_stop(self):
#         if self.driver:
#             self.driver.quit()

#     #TODO improve replace
#     def extract_domain_from_url(self, url):
#         return url.replace('http:', '').replace('https:', '').replace('www.', '').replace('/', '')


#     def add_cookies(self, url):

#         domain_name = self.extract_domain_from_url(url)

#         cookie_file = '{}/../data/cookies_{}.json'.format(
#             os.path.dirname(os.path.abspath(__file__)),
#             domain_name
#         )

#         print('cookie_file: ', cookie_file)

#         # Load the cookies from a JSON file
#         with open(cookie_file) as f:
#             cookies = json.load(f)

#         # Add each cookie to the Selenium session
#         for cookie in cookies:
#             cookie["sameSite"] = str(cookie["sameSite"])
#             print('cookie: ', cookie)
#             self.driver.add_cookie(cookie)


#     def clear_cache(self):

#         self.driver.execute_script("localStorage.clear();")
#         self.driver.execute_script("sessionStorage.clear();")
#         self.driver.delete_all_cookies()


#     def move_to_default_page(self):
#         self.driver.get(os.getenv('DEFAULT_URL'))


#     def load_login_page(self, url):

#         start_time = perf_counter()

#         self.driver.get(url)

#         # waits for title
#         WebDriverWait(self.driver, 15).until(
#             EC.visibility_of_element_located(
#                 (By.CSS_SELECTOR, "span.css-10trblm.e16nr0p30")
#             )
#         )

#         # self.driver.get_screenshot_as_file("./screenshot_title_presence.png")

#         # gets all buttons of page with title
#         buttons = WebDriverWait(self.driver, 30).until(
#             EC.visibility_of_all_elements_located(
#                 (By.CSS_SELECTOR, "button.css-5uatcg.edgvbvh5")
#             )
#         )

#         # self.driver.get_screenshot_as_file("./screenshot_buttons.png")

#         loaded_expected_element = False

#         for button in buttons:
#             if button.text == 'Login':
#                 WebDriverWait(self.driver, 15).until(
#                     EC.element_to_be_clickable(
#                         button
#                     )
#                 )
#                 loaded_expected_element = True
#                 break

#         if not loaded_expected_element:
#             raise Exception('Did not find expected element')

#         return get_execution_time(start_time)
    

#     def load_main_page(self, url):

#         # self.driver.implicitly_wait(10)

#         start_time = perf_counter()

#         self.driver.get(url)

#         self.add_cookies(url)

#         # waits for title
#         WebDriverWait(self.driver, 15).until(
#             EC.visibility_of_element_located(
#                 (By.CSS_SELECTOR, "span.css-10trblm.e16nr0p30")
#             )
#         )

#         # self.driver.get_screenshot_as_file("./screenshot_title_presence.png")

#         loaded_expected_element = False

#         for i in range(10):

#             # gets all buttons of page with title
#             buttons = WebDriverWait(self.driver, 30).until(
#                 EC.visibility_of_all_elements_located(
#                     # (By.CSS_SELECTOR, "button")
#                     (By.CSS_SELECTOR, "button.css-5uatcg.edgvbvh10")
#                 )
#             )

#             # self.driver.get_screenshot_as_file("./screenshot_buttons.png")

#             for button in buttons:
                
#                 try:
#                     if 'Logout' in button.text:
#                         WebDriverWait(self.driver, 15).until(
#                             EC.element_to_be_clickable(
#                                 button
#                             )
#                         )
#                         loaded_expected_element = True
#                         break
#                 except Exception as e:
#                     print('exception: ', e)
#                     # raise
#                     pass

#             if loaded_expected_element:
#                 break

#             sleep(0.5)

#         if not loaded_expected_element:
#             raise Exception('Did not find expected element')

#         return get_execution_time(start_time)


#     def interact_on_login_page(self, url, stage):

#         try:
            
#             load_time = self.load_login_page(url)

#             # Report the request duration to Locust
#             events.request.fire(
#                 request_type="GET", 
#                 name=f"{stage}_load_login_page", 
#                 response_time=load_time, 
#                 response_length=0 #TODO
#             )

#             # TODO: collect interaction metrics

#             self.move_to_default_page()

#         except Exception as e:

#             exception_type = type(e)
            
#             # Report the request duration to Locust
#             events.request.fire(
#                 request_type="GET", 
#                 name=f"{stage}_load_login_page", 
#                 response_time=0, 
#                 response_length=0,
#                 exception=exception_type
#             )

#             raise


#     def interact_on_main_page(self, url, stage):

#         try:
            
#             load_time = self.load_main_page(url)

#             # Report the request duration to Locust
#             events.request.fire(
#                 request_type="GET", 
#                 name=f"{stage}_load_main_page", 
#                 response_time=load_time, 
#                 response_length=0 #TODO
#             )

#             # TODO: collect interaction metrics

#             self.clear_cache()
#             self.move_to_default_page()

#         except Exception as e:
           
#             exception_type = type(e)
            
#             # Report the request duration to Locust
#             events.request.fire(
#                 request_type="GET", 
#                 name=f"{stage}_load_main_page", 
#                 response_time=0, 
#                 response_length=0,
#                 exception=exception_type
#             )

#             raise


#     @task
#     def dev_login_page(self):
#         url = url_from_domain(os.getenv('DOMAIN_DEV'))
#         self.interact_on_login_page(url, stage='dev')

#     @task
#     def prod_login_page(self):
#         url = url_from_domain(os.getenv('DOMAIN_PROD'))
#         self.interact_on_login_page(url, stage='prod')

#     @task
#     def dev_main_page(self):
#         url = url_from_domain(os.getenv('DOMAIN_DEV'))
#         self.interact_on_main_page(url, stage='dev')

#     @task
#     def prod_main_page(self):
#         url = url_from_domain(os.getenv('DOMAIN_PROD'))
#         self.interact_on_main_page(url, stage='prod')


class APITester(HttpUser):
    
    fixed_count = 2

    wait_time = between(1,5)

    def get_api_key(self):
        return os.getenv("API_KEY")

    def get_endpoint_url(self, tablename):
        return f'{self.environment.host}/api/v1/{tablename}?limit=5'.replace('//api', '/api')
    
    def call_endpoint(self, base_url, table_name, query_params, api_key, test_name):

        print('in call_endpoint')

        try:
            query = urllib.parse.urlencode(query_params)
            endpoint = f'{base_url}/api/v1/{table_name}?{query}'.replace('//api', '/api')
            print('endpoint: ', endpoint)
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Accept-Profile": "demo"
            }
            self.client.get(endpoint, headers=headers, name=test_name)

        except Exception as e:

            print(e)

            exception_type = type(e)
            
            # Report the request duration to Locust
            events.request.fire(
                request_type="GET", 
                name=test_name, 
                response_time=0, 
                response_length=0,
                exception=exception_type
            )      

            raise  

    
    @task
    def dev_boalf_5(self):

        api_key = os.getenv('API_KEY_DEV')

        base_url = url_from_domain(os.getenv('DOMAIN_DEV'))

        table_name = 'boalf'

        query_params = {
            "limit": "5",
        }

        self.call_endpoint(base_url, table_name, query_params, api_key, 'API dev_boalf_5')


    # @task
    # def dev_boalf_50000(self):

    #     api_key = os.getenv('API_KEY_DEV')

    #     base_url = url_from_domain(os.getenv('DOMAIN_DEV'))

    #     table_name = 'boalf'

    #     query_params = {
    #         "and": "(settlement_start.gte.2023-03-01T09:00:00+00:00,settlement_start.lte.2023-03-03T09:00:00+00:00)",
    #         "order": "available_at.desc",
    #         "limit": "50000",
    #     }

    #     self.call_endpoint(base_url, table_name, query_params, api_key, 'API dev_boalf_50000')

    
    @task
    def prod_boalf_5(self):

        api_key = os.getenv('API_KEY_PROD')

        base_url = url_from_domain(os.getenv('DOMAIN_PROD'))

        table_name = 'boalf'

        query_params = {
            "limit": "5",
        }

        self.call_endpoint(base_url, table_name, query_params, api_key, 'API prod_boalf_5')


    # @task
    # def prod_boalf_50000(self):

    #     api_key = os.getenv('API_KEY_PROD')

    #     base_url = url_from_domain(os.getenv('DOMAIN_PROD'))

    #     table_name = 'boalf'

    #     query_params = {
    #         "and": "(settlement_start.gte.2023-03-01T09:00:00+00:00,settlement_start.lte.2023-03-03T09:00:00+00:00)",
    #         "order": "available_at.desc",
    #         "limit": "50000",
    #     }

    #     self.call_endpoint(base_url, table_name, query_params, api_key, 'API prod_boalf_50000')


    # @task
    # def dev_b1770_5(self):

    #     api_key = os.getenv('API_KEY_DEV')

    #     base_url = url_from_domain(os.getenv('DOMAIN_DEV'))

    #     table_name = 'b1770'

    #     query_params = {
    #         "limit": "5",
    #     }

    #     self.call_endpoint(base_url, table_name, query_params, api_key, 'API dev_b1770_5')


    # @task
    # def dev_b1770_50000(self):

    #     api_key = os.getenv('API_KEY_DEV')

    #     base_url = url_from_domain(os.getenv('DOMAIN_DEV'))

    #     table_name = 'b1770'

    #     query_params = {
    #         "and": "(settlement_start.gte.2023-03-01T09:00:00+00:00,settlement_start.lte.2023-03-03T09:00:00+00:00)",
    #         "order": "available_at.desc",
    #         "limit": "50000",
    #     }

    #     self.call_endpoint(base_url, table_name, query_params, api_key, 'API dev_b1770_50000')

    
    # @task
    # def prod_b1770_5(self):

    #     api_key = os.getenv('API_KEY_PROD')

    #     base_url = url_from_domain(os.getenv('DOMAIN_PROD'))

    #     table_name = 'b1770'

    #     query_params = {
    #         "limit": "5",
    #     }

    #     self.call_endpoint(base_url, table_name, query_params, api_key, 'API prod_b1770_5')


    # @task
    # def prod_b1770_50000(self):

    #     api_key = os.getenv('API_KEY_PROD')

    #     base_url = url_from_domain(os.getenv('DOMAIN_PROD'))

    #     table_name = 'b1770'

    #     query_params = {
    #         "and": "(settlement_start.gte.2023-03-01T09:00:00+00:00,settlement_start.lte.2023-03-03T09:00:00+00:00)",
    #         "order": "available_at.desc",
    #         "limit": "50000",
    #     }

    #     self.call_endpoint(base_url, table_name, query_params, api_key, 'API prod_b1770_50000')


    # @task
    # def dev_pn_5(self):

    #     api_key = os.getenv('API_KEY_DEV')

    #     base_url = url_from_domain(os.getenv('DOMAIN_DEV'))

    #     table_name = 'pn'

    #     query_params = {
    #         "limit": "5",
    #     }

    #     self.call_endpoint(base_url, table_name, query_params, api_key, 'API dev_pn_5')


    # @task
    # def dev_pn_50000(self):

    #     api_key = os.getenv('API_KEY_DEV')

    #     base_url = url_from_domain(os.getenv('DOMAIN_DEV'))

    #     table_name = 'pn'

    #     query_params = {
    #         "and": "(settlement_start.gte.2023-03-01T09:00:00+00:00,settlement_start.lte.2023-03-03T09:00:00+00:00)",
    #         "order": "available_at.desc",
    #         "limit": "50000",
    #     }

    #     self.call_endpoint(base_url, table_name, query_params, api_key, 'API dev_pn_50000')

    
    # @task
    # def prod_pn_5(self):

    #     api_key = os.getenv('API_KEY_PROD')

    #     base_url = url_from_domain(os.getenv('DOMAIN_PROD'))

    #     table_name = 'pn'

    #     query_params = {
    #         "limit": "5",
    #     }

    #     self.call_endpoint(base_url, table_name, query_params, api_key, 'API prod_pn_5')


    # @task
    # def prod_pn_50000(self):

        api_key = os.getenv('API_KEY_PROD')

        base_url = url_from_domain(os.getenv('DOMAIN_PROD'))

        table_name = 'pn'

        query_params = {
            "and": "(settlement_start.gte.2023-03-01T09:00:00+00:00,settlement_start.lte.2023-03-03T09:00:00+00:00)",
            "order": "available_at.desc",
            "limit": "50000",
        }

        self.call_endpoint(base_url, table_name, query_params, api_key, 'API prod_pn_50000')