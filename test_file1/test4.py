from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Set up Selenium
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Step 2: Navigate & Scrape
driver.get('https://rera.odisha.gov.in/projectlist')
time.sleep(5)  # Adjust as needed

projects = []
for i in range(1, 6):  # Adjust range for more pages/projects
    try:
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = soup.select('.project-box')
        for card in cards:
            title = card.select_one('h4').text.strip()
            builder = card.select_one('p').text.strip()
            projects.append({'Project': title, 'Builder': builder})
    except Exception as e:
        print(f"Error: {e}")

driver.quit()

# Step 3: Data Cleaning
df = pd.DataFrame(projects).drop_duplicates()
df.dropna(inplace=True)

# Step 4: Encode and Cluster
le = LabelEncoder()
df['Builder_encoded'] = le.fit_transform(df['Builder'])

kmeans = KMeans(n_clusters=3, random_state=42)
df['Cluster'] = kmeans.fit_predict(df[['Builder_encoded']])

# Step 5: Visualize
sns.countplot(data=df, x='Cluster')
plt.title("Project Clusters by Builder")
plt.show()

# Step 6: Save to CSV
df.to_csv('odisha_rera_projects.csv', index=False)