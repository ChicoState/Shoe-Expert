from django.test import TestCase
from django.test import LiveServerTestCase
from selenium import WebDriver
from selenium.webdriver.common.keys import Keys

# Create your tests here.

class LoginFormTest(LiveServerTestCase):

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


class JoinFormTest(LiveServerTestCase):

  def testLogin(self):
    selenium = webdriver.Chrome()
    #Choose your url to visit
    selenium.get('http://127.0.0.1:8000/join')
    #find the elements you need to submit form
    username = selenium.find_element_by_id('username')
    password = selenium.find_element_by_id('password')
    first_name = selenium.find_element_by_id('name')
    last_name = selenium.find_element_by_id('name')
    email = selenium.find_element_by_id('email')

    submit = selenium.find_element_by_id('join')

    #populate the form with data
    username.send_keys('testUser')
    password.send_keys('testPass')
    first_name.send_keys('firstName')
    last_name.send_keys('lastName')
    email.send_keys('test@gmail.com')

    #submit form
    submit.send_keys(Keys.RETURN)

    #check result; page source looks at entire html document
    assert 'testUser' in selenium.page_source
