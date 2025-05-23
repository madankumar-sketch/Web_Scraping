import os
import time
import csv
import re
from PIL import Image
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ===== CONFIGURATION =====
SCREENSHOT_DIR = os.path.abspath("screenshots")  # Absolute path for Windows
CSV_FILE = "rera_projects.csv"
WEBSITE_URL = "https://rera.odisha.gov.in"
PROJECT_SELECTOR = ".project-item"  # UPDATE THIS AFTER INSPECTION
MAX_PROJECTS = 6
WAIT_TIME = 5

def setup_environment():
    """Initialize directories and Tesseract"""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    # Windows-specific Tesseract path
    if os.name == 'nt':
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            print(f"❌ Tesseract not found at {tesseract_path}")
            print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            exit()

def initialize_driver():
    """Configure Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Windows-specific Chrome options
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.implicitly_wait(10)
    return driver

def take_screenshot(driver, path):
    """Take screenshot and return PIL Image"""
    driver.save_screenshot(path)
    return Image.open(path).convert('L')  # Convert to grayscale

def extract_data_from_text(text):
    """Improved data extraction with regex"""
    patterns = {
        'RERA_Regd_No': r'RERA\s*Reg(?:istration|d\.?)\s*No\.?:\s*([A-Za-z0-9/-]+)',
        'Project_Name': r'Project\s*Name:\s*(.+?)(?=\n|$)',
        'Company_Name': r'Company\s*Name:\s*(.+?)(?=\n|$)',
        'Registered_Office_Address': r'Registered\s*Office\s*Address:\s*(.+?)(?=\n|$)',
        'GST_NO': r'GST\s*No\.?:\s*([A-Z0-9]+)'
    }
    
    data = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        data[field] = match.group(1).strip() if match else "NOT_FOUND"
    return data

def main():
    print("=== RERA Odisha Scraper ===")
    setup_environment()
    
    driver = initialize_driver()
    try:
        # Step 1: Load website
        print(f"\n🌐 Loading {WEBSITE_URL}...")
        driver.get(WEBSITE_URL)
        time.sleep(WAIT_TIME)  # Critical for slow connections
        
        # Step 2: Find projects
        print("\n🔍 Searching for projects...")
        projects = driver.find_elements(By.CSS_SELECTOR, PROJECT_SELECTOR)[:MAX_PROJECTS]
        print(f"✅ Found {len(projects)} projects")
        
        if not projects:
            print("❌ No projects found! Possible issues:")
            print(f"- Wrong selector: Current selector is '{PROJECT_SELECTOR}'")
            print("- Page didn't load properly (check screenshots/homepage.png)")
            driver.save_screenshot(os.path.join(SCREENSHOT_DIR, "homepage.png"))
            return
        
        # Step 3: Process projects
        project_data = []
        for idx, project in enumerate(projects, 1):
            try:
                print(f"\n📦 Processing project {idx}/{len(projects)}")
                
                # Click project (with JavaScript as fallback)
                try:
                    project.click()
                except:
                    driver.execute_script("arguments[0].click();", project)
                time.sleep(WAIT_TIME)
                
                # Take and process screenshot
                ss_path = os.path.join(SCREENSHOT_DIR, f"project_{idx}.png")
                img = take_screenshot(driver, ss_path)
                print(f"📸 Screenshot saved to {ss_path}")
                
                # OCR extraction
                text = pytesseract.image_to_string(img)
                with open(f"{SCREENSHOT_DIR}/project_{idx}_text.txt", "w", encoding="utf-8") as f:
                    f.write(text)  # Save raw OCR output for debugging
                
                # Data extraction
                data = extract_data_from_text(text)
                project_data.append(data)
                print("📊 Extracted data:", data)
                
                # Return to main page
                driver.back()
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ Error on project {idx}: {str(e)}")
                continue
        
        # Step 4: Save results
        if project_data:
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=project_data[0].keys())
                writer.writeheader()
                writer.writerows(project_data)
            print(f"\n💾 Success! Data saved to {CSV_FILE}")
        else:
            print("\n❌ No data extracted. Check screenshots folder for debugging.")
            
    finally:
        driver.quit()
        print("\n🛑 Browser closed")

if __name__ == "__main__":
    main()