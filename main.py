import os
import csv
import smtplib
import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Load Google Sheets creds from GitHub Secret
gservice_json = json.loads(os.environ['GSHEET_CREDENTIALS_JSON'])

# Load mappings from config
with open("sheet_map.json", "r") as f:
    sheet_map = json.load(f)

# SMTP Email config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.environ["SMTP_EMAIL"]
EMAIL_PASS = os.environ["SMTP_PASS"]

FB_EMAIL = os.environ["FB_EMAIL"]
FB_PASS = os.environ["FB_PASS"]

def send_email(recipients, subject, body, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, "rb") as f:
        part = MIMEApplication(f.read(), Name="leads.csv")
        part['Content-Disposition'] = 'attachment; filename="leads.csv"'
        msg.attach(part)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.send_message(msg)
    server.quit()
    print(f"✅ Email sent to: {recipients}")

def write_to_sheet(sheet_name, worksheet_name, data_rows):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(gservice_json, scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name).worksheet(worksheet_name)
    sheet.append_rows(data_rows, value_input_option="USER_ENTERED")
    print(f"✅ Sheet '{sheet_name}' updated with {len(data_rows)} rows.")

def login_facebook(driver):
    driver.get("https://www.facebook.com/login")
    time.sleep(3)
    driver.find_element(By.ID, "email").send_keys(FB_EMAIL)
    driver.find_element(By.ID, "pass").send_keys(FB_PASS + Keys.RETURN)
    time.sleep(5)

def download_csv(driver):
    # Replace with the actual URL of your lead form's download center
    lead_url = "https://business.facebook.com/latest/leads_center/"
    driver.get(lead_url)
    time.sleep(10)
    try:
        download_btn = driver.find_element(By.XPATH, "//div[contains(text(),'Download')]")
        download_btn.click()
        time.sleep(2)
        csv_btn = driver.find_element(By.XPATH, "//span[contains(text(),'CSV')]")
        csv_btn.click()
        time.sleep(5)
        print("✅ CSV Downloaded")
        return True
    except:
        print("❌ Failed to trigger download")
        return False

def parse_and_distribute():
    filepath = "leads.csv"
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    form_id = rows[0].get("Form ID", "default")
    config = sheet_map.get(form_id)

    if not config:
        print(f"⚠️ No config found for form ID {form_id}")
        return

    mapped_rows = []
    for r in rows:
        mapped_rows.append([
            r.get("Full Name", ""),
            r.get("Email", ""),
            r.get("Phone Number", ""),
            r.get("City", ""),
            r.get("Business Type/Industry", ""),
            r.get("Campaign Name", ""),
            r.get("Ad Name", ""),
            r.get("Created Time", "")
        ])

    write_to_sheet(config["sheet_name"], config["tab_name"], mapped_rows)
    send_email([config["email"]], f"New Leads from {form_id}", "See attached CSV", filepath)

def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        login_facebook(driver)
        if download_csv(driver):
            parse_and_distribute()
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
