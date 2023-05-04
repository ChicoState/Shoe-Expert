from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

service = ChromeService(executable_path=ChromeDriverManager().install())

driver = webdriver.Chrome(service=service)

# Create your tests here.

class LoginFormTest(testCase):
    def testform(self):
       selenium.get('http://127.0.0.1:8000/')
       username=selenium.find_element_by_id('username')
       password=selenium.find_element_by_id('password')

       submit = selenium.find_element_by_id('submit_button')

       username.send_keys('docker')
       password.send_keys('docker')

       submit.send_keys(Keys.RETURN)

       assert 'docker' in selenium.page_source

driver.quit();
