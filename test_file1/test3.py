
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

driver = webdriver.Chrome()
driver.get("https://rera.odisha.gov.in/projects/project-list")
time.sleep(3)

projects_data = []

for i in range(1, 7):
    try:
        driver.get("https://rera.odisha.gov.in/projects/project-list")
        time.sleep(3)
        element = driver.find_element(By.XPATH, f"(//a[contains(text(),'View Details')])[{i}]")
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)
        element.click()
        time.sleep(3)

        data = {}
        data["RERA Regd. No"] = driver.find_element(By.XPATH, "//td[contains(text(),'RERA Regd. No')]/following-sibling::td").text
        data["Project Name"] = driver.find_element(By.XPATH, "//td[contains(text(),'Project Name')]/following-sibling::td").text
        data["Promoter Name"] = driver.find_element(By.XPATH, "//a[contains(@href,'promoter-details')]").text

        # Go to promoter details
        driver.find_element(By.XPATH, "//a[contains(text(),'Promoter Details')]").click()
        time.sleep(2)

        data["Promoter Company"] = driver.find_element(By.XPATH, "//td[contains(text(),'Company Name')]/following-sibling::td").text
        data["Promoter Address"] = driver.find_element(By.XPATH, "//td[contains(text(),'Registered Office Address')]/following-sibling::td").text
        data["GST No"] = driver.find_element(By.XPATH, "//td[contains(text(),'GST No')]/following-sibling::td").text

        projects_data.append(data)

    except Exception as e:
        print(f"Error extracting project {i}: {e}")

driver.quit()

df = pd.DataFrame(projects_data)
df.to_csv("odisha_rera_projects.csv", index=False)
print("Data saved to 'odisha_rera_projects.csv'")
