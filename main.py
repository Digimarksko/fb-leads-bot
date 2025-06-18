import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

FB_EMAIL = os.environ['FB_EMAIL']
FB_PASS = os.environ['FB_PASS']

# Replace this with the actual leads center URL of your Facebook Page
LEADS_CENTER_URL = "https://business.facebook.com/latest/leads_center?business_id=9016010605180123&asset_id=569918452860655"

def setup_browser():
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1920,1080")
    return uc.Chrome(options=options)

def login_facebook(driver):
    driver.get("https://www.facebook.com/login")
    time.sleep(3)

    email_input = driver.find_element(By.ID, "email")
    email_input.send_keys(FB_EMAIL)
    password_input = driver.find_element(By.ID, "pass")
    password_input.send_keys(FB_PASS)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

    if "checkpoint" in driver.current_url or "login" in driver.current_url:
        print("⚠️ Login failed or checkpoint triggered.")
        driver.quit()
        return False
    print("✅ Logged into Facebook.")
    return True

def download_leads(driver):
    driver.get(LEADS_CENTER_URL)
    time.sleep(8)

    try:
        download_button = driver.find_element(By.XPATH, "//div[contains(text(),'Download')]")
        download_button.click()
        time.sleep(2)
        csv_button = driver.find_element(By.XPATH, "//span[contains(text(),'CSV')]")
        csv_button.click()
        print("✅ CSV download triggered.")
        time.sleep(5)
    except Exception as e:
        print("❌ Failed to download leads:", e)

def main():
    driver = setup_browser()
    if login_facebook(driver):
        download_leads(driver)
    driver.quit()

if __name__ == "__main__":
    main()
