from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import os
import base_test

class VerifyHeader000000002(base_test.BaseTest):
    def test_verify_header000000002(self):
        driver = self.driver
        driver.get(self.base_url + "/login/")
        driver.find_element_by_id("id_username").clear()
        driver.find_element_by_id("id_username").send_keys("varify")
        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys("varify")
        driver.find_element_by_xpath("//input[@value='Login']").click()
        driver.find_element_by_link_text("Varify").click()
        driver.find_element_by_link_text("Workspace").click()
        driver.find_element_by_link_text("Discover").click()
        driver.find_element_by_link_text("Results").click()
        driver.find_element_by_css_selector("b.caret").click()
        driver.find_element_by_link_text("Logout").click()
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
