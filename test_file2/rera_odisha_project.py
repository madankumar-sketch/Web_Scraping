from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

# Setup Chrome WebDriver (ensure ChromeDriver is installed and in PATH)
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service()  # optionally specify path to chromedriver here

driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the RERA Odisha project list page
url = "https://rera.odisha.gov.in/projects/project-list"
driver.get(url)
time.sleep(3)

# Collect data from first 6 projects
projects_data = []
for i in range(1, 7):
    try:
        # Click "View Details" for each project
        view_button = driver.find_element(By.XPATH, f"(//a[contains(text(),'View Details')])[{i}]")
        view_button.click()
        time.sleep(3)

        # Extract the required fields
        data = {}
        data["RERA Regd. No"] = driver.find_element(By.XPATH, "//td[contains(text(),'RERA Regd. No')]/following-sibling::td").text
        data["Project Name"] = driver.find_element(By.XPATH, "//td[contains(text(),'Project Name')]/following-sibling::td").text
        data["Promoter Name"] = driver.find_element(By.XPATH, "//a[contains(@href,'promoter-details')]").text
        driver.find_element(By.XPATH, "//a[contains(text(),'Promoter Details')]").click()
        time.sleep(2)
        data["Promoter Company"] = driver.find_element(By.XPATH, "//td[contains(text(),'Company Name')]/following-sibling::td").text
        data["Promoter Address"] = driver.find_element(By.XPATH, "//td[contains(text(),'Registered Office Address')]/following-sibling::td").text
        data["GST No"] = driver.find_element(By.XPATH, "//td[contains(text(),'GST No')]/following-sibling::td").text

        projects_data.append(data)
        driver.back()
        time.sleep(3)
    except Exception as e:
        print(f"Error extracting project {i}: {e}")
        driver.back()
        time.sleep(3)

driver.quit()

# Save or display results
df = pd.DataFrame(projects_data)
print(df)

# Optionally export to CSV
df.to_csv("rera_odisha_projects.csv", index=False)