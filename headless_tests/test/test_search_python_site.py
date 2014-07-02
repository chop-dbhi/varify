import unittest
import base_test
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class PythonSiteSearch(base_test.BaseTest):

    def test_search_python(self):
        driver = self.driver
        driver.get("http://python.org")
        time.sleep(5)


        # Search for Selenium
        search_field = driver.find_element_by_name('q')
        search_field.send_keys("Selenium")
        search_field.send_keys(Keys.RETURN)
        time.sleep(3)

        # Click on the first result
        first_result = driver.find_element_by_partial_link_text("Python Job Board")
        first_result.click()
        time.sleep(3)

        # Get RSS Feed
        try:
            rss_feed = driver.find_element_by_link_text("RSS feed")
            rss_feed.click()
        except:
            assert 0, "You must have gone to the wrong page!"

        print "done search on Python site"
    

if __name__ == "__main__":
    unittest.main()
