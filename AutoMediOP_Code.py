import os
import time
import datetime
import traceback
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(filename='automation_debug.log', level=logging.INFO, # login setup
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Script started")

USERNAME = "Username..." # Configuration
PASSWORD = "Pwd..."    

LOGIN_URL = "https://md.healthplix.com/index.php" 
INTERMEDIATE_URL = "https://md.healthplix.com/report/viewCDBillingReport.php?branch_selector=0"

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
start_of_year = datetime.date(today.year, 4, 1)

fdate_str = start_of_year.strftime("%Y-%m-%d")
tdate_str = yesterday.strftime("%Y-%m-%d")

FINAL_REPORT_URL = (
    "https://md.healthplix.com/report/viewFDBillingReport.php?"
    f"s_range=0&fdate={fdate_str}&tdate={tdate_str}&category=0&employee=0&ftime=&ttime="
)

download_dir = r"D:\...."# Output directory

options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.automatic_downloads": 1,
}
options.add_experimental_option("prefs", prefs)

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

def random_sleep(min_seconds=2.5, max_seconds=5.0):
    sleep_time = random.uniform(min_seconds, max_seconds)
    logging.info(f"Sleeping for {sleep_time:.2f} seconds")
    time.sleep(sleep_time)

def wait_for_page_load(max_retries=3, wait_time=30):
    for attempt in range(max_retries):
        page_source = driver.page_source
        if "Server seems to be busy" in page_source:
            logging.warning("Server busy message detected. Waiting before retrying...")
            print("Server busy message detected. Waiting before retrying...")
            time.sleep(wait_time)
            driver.refresh()
            time.sleep(wait_time / 2)
        else:
            return True
    return False

def download_report(tab_xpath, report_filename, do_refresh=True):
    try:
        tab = wait.until(EC.element_to_be_clickable((By.XPATH, tab_xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", tab)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", tab)
        logging.info(f"Tab {tab_xpath} clicked.")
        print(f"Tab {tab_xpath} clicked.")
        time.sleep(3)
        
           if do_refresh:  # Refresh and re-click tab
            driver.refresh()
            time.sleep(3)
            tab = wait.until(EC.element_to_be_clickable((By.XPATH, tab_xpath)))
            driver.execute_script("arguments[0].scrollIntoView(true);", tab)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", tab)
            logging.info(f"Tab {tab_xpath} clicked after refresh.")
            print(f"Tab {tab_xpath} clicked after refresh.")
            time.sleep(3)
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//table/tbody/tr[1]")))
        logging.info(f"Data for {report_filename} is present.")
        print(f"Data for {report_filename} is present.")
        
        all_download_buttons = driver.find_elements(
            By.XPATH, "//a[@title='Download Report' and contains(@onclick, 'downloadTableToCSV')]"
        )
        visible_buttons = [btn for btn in all_download_buttons if btn.is_displayed()]
        
        if not visible_buttons:
            logging.error("No visible download button found for " + report_filename)
            print("No visible download button found for", report_filename)
            return False
        
        chosen_btn = visible_buttons[-1]
        driver.execute_script("arguments[0].scrollIntoView(true);", chosen_btn)
        time.sleep(1)
        try:
            driver.execute_script("arguments[0].click();", chosen_btn)
            logging.info(f"Clicked the download button for {report_filename}.")
            print(f"Clicked the download button for {report_filename}.")
        except Exception as e:
            logging.warning(f"JS click() failed for {report_filename}: {e}. Trying native click()...")# Fallback to native click if JS click times out or fails
            print(f"JS click() failed for {report_filename}: {e}. Trying native click()...")
            chosen_btn.click()
            logging.info(f"Clicked the download button for {report_filename} using native click().")
            print(f"Clicked the download button for {report_filename} using native click().")
       
        before_files = set(os.listdir(download_dir))# Wait for the file to download
        timeout = 60
        downloaded_file = None
        
        for _ in range(timeout):
            time.sleep(1)
            after_files = set(os.listdir(download_dir))
            new_files = after_files - before_files
            for file in new_files:
                if not file.endswith(".crdownload"): # Ignore partial downloads
                    downloaded_file = file
                    break
            if downloaded_file:
                break
        
        if downloaded_file:
            src = os.path.join(download_dir, downloaded_file)
            dst = os.path.join(download_dir, report_filename)
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(src, dst)
            logging.info(f"Downloaded file renamed to: {dst}")
            print(f"Downloaded file renamed to: {dst}")
            leftover_file = os.path.join(download_dir, "report.xlsx")#remove leftover "report.xlsx" if it's a duplicate
            if os.path.exists(leftover_file) and leftover_file != dst:
                if os.path.getsize(leftover_file) == os.path.getsize(dst):# Compare file sizes, if they match, we assume it's a duplicate
                    os.remove(leftover_file)
                    logging.info("Removed leftover 'report.xlsx' as it was a duplicate of Bills_report.")
                    print("Removed leftover 'report.xlsx' as it was a duplicate of Bills_report.")
            
            return True
        else:
            logging.error("Download did not complete within the timeout period for " + report_filename)
            print("Download did not complete within the timeout period for", report_filename)
            return False
        
    except Exception as ex:
        logging.exception("Error in download_report for " + report_filename + ": " + str(ex))
        print("Error in download_report for", report_filename, ":", ex)
        print(traceback.format_exc())
        return False

try:
    # STEP 1: LOGIN
    driver.get(LOGIN_URL)
    wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "loginButton").click()
    wait.until(EC.url_contains("viewFrontdeskDashboard"))
    logging.info("Login successful.")
    print("Login successful.")

    if not wait_for_page_load():
        logging.error("Page did not load properly after login. Exiting.")
        print("Page did not load properly after login. Exiting.")
        driver.quit()
        exit()

    # STEP 2: Navigate to Intermediate Page
    driver.get(INTERMEDIATE_URL)
    time.sleep(5)
    logging.info("Navigated to CD Billing Report Page.")
    print("Navigated to CD Billing Report Page.")

    # STEP 3: Navigate to Final FD Billing Report Page
    driver.execute_script("window.location.href = arguments[0];", FINAL_REPORT_URL)
    time.sleep(5)
    logging.info("Navigated to FD Billing Report Page.")
    print("Navigated to FD Billing Report Page.")

    if not wait_for_page_load():
        logging.error("Final report page did not load properly due to busy server message. Exiting.")
        print("Final report page did not load properly due to busy server message. Exiting.")
        driver.quit()
        exit()

    # Define the tabs
    tabs = [
        {"tab_xpath": "//a[normalize-space(text())='Bills']", "report_filename": "Bills_report.xlsx", "refresh": True},
        {"tab_xpath": "//a[normalize-space(text())='Collections']", "report_filename": "Collections_report.xlsx", "refresh": False},
        {"tab_xpath": "//a[normalize-space(text())='Refunds']", "report_filename": "Refunds_report.xlsx", "refresh": False},
        {"tab_xpath": "//a[normalize-space(text())='Cancelled Bills']", "report_filename": "Cancelled_report.xlsx", "refresh": False}
    ]

    for tab in tabs:
        logging.info("==========================================")
        print("\n==========================================")
        logging.info(f"Processing report for: {tab['report_filename']}")
        print(f"Processing report for: {tab['report_filename']}")
        success = download_report(tab["tab_xpath"], tab["report_filename"], do_refresh=tab["refresh"])
        if success:
            logging.info(f"Successfully downloaded {tab['report_filename']}.")
            print(f"Successfully downloaded {tab['report_filename']}.")
        else:
            logging.error(f"Failed to download {tab['report_filename']}.")
            print(f"Failed to download {tab['report_filename']}.")
        time.sleep(5)
        random_sleep()

except Exception as e:
    logging.exception("Script failed due to an error: " + str(e))
    print("Script failed due to an error:", e)
    print(traceback.format_exc())
finally:
    driver.quit()
    logging.info("Browser closed.")
    print("Browser closed.")
