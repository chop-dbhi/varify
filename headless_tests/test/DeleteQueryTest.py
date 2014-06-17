from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, \
    NoAlertPresentException
import unittest, time, re


class DeleteQueryTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.PhantomJS()
        self.driver.implicitly_wait(30)
        self.base_url = "http://0.0.0.0:8000/login/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_delete_query(self):
        driver = self.driver
        driver.set_window_size(1440, 900)
        driver.get(self.base_url)
        driver.find_element_by_id("id_username").clear()
        driver.find_element_by_id("id_username").send_keys("user003")
        driver.find_element_by_id("id_password").clear()
        driver.find_element_by_id("id_password").send_keys("chopchop")
        driver.find_element_by_xpath("//input[@value='Login']").click()
        for i in range(60):
            try:
                if self.is_element_present(By.CSS_SELECTOR, "div.query-list"):
                    break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")
        driver.find_element_by_link_text("Results").click()
        driver.find_element_by_xpath("//div[@id='content']/div[10]/div/div/div/button[3]").click()
        driver.find_element_by_xpath("//div[@id='content']/div[5]/div[3]/button[2]").click()
        driver.find_element_by_link_text("Workspace").click()
        for i in range(60):
            try:
                if self.is_element_present(By.CSS_SELECTOR, "span.name-label"):
                    break
            except:
                pass
            time.sleep(1)
        else:
            self.fail("time out")
        driver.find_element_by_xpath("//div[@id='content']/div[9]/div/div/div/div/div[5]/div[2]/span[2]/button[2]").click()
        driver.find_element_by_xpath("//div[@id='content']/div[6]/div[3]/button[2]").click()
        driver.find_element_by_link_text("user003").click()
        driver.find_element_by_link_text("Logout").click()

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException:
            return False
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
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
