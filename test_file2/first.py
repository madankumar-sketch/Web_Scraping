import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
OUTPUT_CSV = 'rera_projects.csv'
SCREENSHOT_DIR = 'screenshots'
WEBSITE_URL = 'https://rera.odisha.gov.in/projects/project-list'
MAX_PROJECTS = 6

def setup_environment():
    """Create necessary directories"""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def initialize_driver():
    """Initialize and configure Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    
    # Uncomment for headless mode
    # chrome_options.add_argument("--headless=new")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.implicitly_wait(10)
    return driver

def scrape_project_details(driver, project_url):
    """Scrape details from individual project page"""
    driver.get(project_url)
    time.sleep(3)  # Wait for page to load
    
    # Initialize data dictionary
    project_data = {
        'RERA_Regd_No': 'NOT_FOUND',
        'Project_Name': 'NOT_FOUND',
        'Promoter_Name': 'NOT_FOUND',
        'Registered_Office_Address': 'NOT_FOUND',
        'GST_NO': 'NOT_FOUND'
    }
    
    try:
        # Extract basic info
        project_data['RERA_Regd_No'] = driver.find_element(By.CSS_SELECTOR, "div.project-details h2").text.split(':')[-1].strip()
        project_data['Project_Name'] = driver.find_element(By.CSS_SELECTOR, "div.project-details h1").text.strip()
        
        # Click on Promoter Details tab
        promoter_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Promoter Details')]"))
        )
        promoter_tab.click()
        time.sleep(2)
        
        # Extract promoter info
        project_data['Promoter_Name'] = driver.find_element(By.XPATH, "//th[contains(text(),'Company Name')]/following-sibling::td").text.strip()
        project_data['Registered_Office_Address'] = driver.find_element(By.XPATH, "//th[contains(text(),'Registered Office')]/following-sibling::td").text.strip()
        project_data['GST_NO'] = driver.find_element(By.XPATH, "//th[contains(text(),'GST No')]/following-sibling::td").text.strip()
        
    except Exception as e:
        print(f"⚠️ Error extracting details: {str(e)}")
    
    return project_data

def main():
    print("=== RERA Odisha Project Scraper ===")
    setup_environment()
    
    driver = initialize_driver()
    try:
        # Step 1: Load project list page
        print(f"\n🌐 Loading project list: {WEBSITE_URL}")
        driver.get(WEBSITE_URL)
        time.sleep(5)  # Wait for page to load
        
        # Step 2: Find all project links
        print("\n🔍 Finding projects...")
        project_links = []
        projects = driver.find_elements(By.CSS_SELECTOR, "table#projectTable tbody tr a")[:MAX_PROJECTS]
        
        for project in projects:
            project_links.append(project.get_attribute('href'))
        
        print(f"✅ Found {len(project_links)} projects")
        
        if not project_links:
            print("❌ No projects found! Possible issues:")
            print("- Website structure changed")
            print("- Page didn't load properly")
            driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "homepage.png"))
            return
        
        # Step 3: Process each project
        project_data = []
        for idx, url in enumerate(project_links, 1):
            try:
                print(f"\n📦 Processing project {idx}/{len(project_links)}")
                print(f"🔗 URL: {url}")
                
                data = scrape_project_details(driver, url)
                project_data.append(data)
                print("📊 Extracted data:", data)
                
                # Take screenshot
                ss_path = os.path.join(SCREENSHOT_DIR, f"project_{idx}.png")
                driver.save_screenshot(ss_path)
                print(f"📸 Screenshot saved to {ss_path}")
                
            except Exception as e:
                print(f"⚠️ Error processing project {idx}: {str(e)}")
                continue
        
        # Step 4: Save results to CSV
        if project_data:
            with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=project_data[0].keys())
                writer.writeheader()
                writer.writerows(project_data)
            print(f"\n💾 Success! Data saved to {OUTPUT_CSV}")
        else:
            print("\n❌ No data extracted. Check screenshots folder for debugging.")
            
    finally:
        driver.quit()
        print("\n🛑 Browser closed")

if __name__ == "__main__":
    main()