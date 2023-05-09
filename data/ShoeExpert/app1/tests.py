from django.test import TestCase
from django.test import LiveServerTestCase
from selenium import WebDriver
from selenium.webdriver.common.keys import Keys

# Create your tests here.

class PlayerFormTest(LiveServerTestCase):

  def testLogin(self):
    selenium = webdriver.Chrome()
    #Choose your url to visit
    selenium.get('http://127.0.0.1:8000/')
    #find the elements you need to submit form
    username = selenium.find_element_by_id('username')
    password = selenium.find_element_by_id('password')

    submit = selenium.find_element_by_id('login')

    #populate the form with data
    username.send_keys('docker')
    password.send_keys('docker')

    #submit form
    submit.send_keys(Keys.RETURN)

    #check result; page source looks at entire html document
    body = self.browser.find_element_by_tag_name('body')
    self.assertIn('Home', body.text)
