import requests
from bs4 import BeautifulSoup
import csv

# Target website
base_url = "https://rera.odisha.gov.in"
project_list_url = f"{base_url}/projects/project-list"

# Headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0"
}

# Step 1: Get the main project list page
response = requests.get(project_list_url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Step 2: Find the first 6 project detail links
project_links = []
all_links = soup.select('a[href*="/projects/view-project-details"]')

print(f"Found {len(all_links)} project links.")

for link_tag in all_links[:6]:
    href = link_tag.get("href")
    if href:
        full_link = base_url + href
        project_links.append(full_link)

print("Project links collected:", project_links)

# Step 3: Open CSV file for writing
with open("rera_projects.csv", mode="w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["RERA No", "Project Name", "Promoter Name", "Promoter Address", "GST No"])

    # Step 4: Visit each project's detail page and extract info
    for link in project_links:
        print(f"Fetching: {link}")
        response = requests.get(link, headers=headers)
        detail_soup = BeautifulSoup(response.text, "html.parser")

        try:
            def get_text(label):
                cell = detail_soup.find("td", string=label)
                return cell.find_next("td").text.strip() if cell else "N/A"

            rera_no = get_text("RERA Regd. No.")
            project_name = get_text("Project Name")
            promoter_name = get_text("Company Name")
            promoter_address = get_text("Registered Office Address")
            gst_no = get_text("GST No.")

            print("Project:", project_name)
            writer.writerow([rera_no, project_name, promoter_name, promoter_address, gst_no])

        except Exception as e:
            print("Error processing project:", link)
            print(e)