import unittest
import base_test
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class GoogleSearch(base_test.BaseTest):

    def test_search_google(self):
        driver = self.driver
        driver.get("http://www.google.ro/")
        time.sleep(5)

        # Search for Python
        search_field = driver.find_element_by_name('q')
        search_field.send_keys("Python")
        search_field.send_keys(Keys.RETURN)
        time.sleep(3)

        # Click on the first result
        first_result = driver.find_element_by_partial_link_text("Official Website")
        first_result.click()
        time.sleep(3)
        print "done test - search on google"

        # Assert text is present on page
	try:
		assert "Python" in driver.title
	except:
		assert 0, "You must have gone to the wrong page!"
    

if __name__ == "__main__":
    unittest.main()
