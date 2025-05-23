
import requests
from bs4 import BeautifulSoup
import csv  # To help save data in a table (CSV file)

# This is the website we want to visit
main_website = "https://rera.odisha.gov.in"
project_list_page = main_website + "/projects/project-list"

# This makes the website think we are using a real browser (so it gives us the correct page)
headers = {
    "User-Agent": "Mozilla/5.0"
}

#Open the project list page
response = requests.get(project_list_page, headers=headers)
page = BeautifulSoup(response.text, "html.parser")  # Read the page like a book

# Step 2: Find the first 6 project links from the page
project_links = []
all_links = page.select('a[href*="/projects/view-project-details"]')  # Find all project detail links

# Only take the first 6 projects
for link in all_links[:6]:
    full_link = main_website + link['href']
    project_links.append(full_link)

# Step 3: Create a new CSV file to save the project data
with open("rera_projects.csv", mode="w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)

    # Write the table header (column names)
    writer.writerow(["RERA No", "Project Name", "Promoter Name", "Promoter Address", "GST No"])

    # Step 4: Visit each project's page and collect details
    for project_url in project_links:
        response = requests.get(project_url, headers=headers)
        project_page = BeautifulSoup(response.text, "html.parser")

        try:
            # Read the information from the page
            rera_no = project_page.find("td", string="RERA Regd. No.").find_next("td").text.strip()
            project_name = project_page.find("td", string="Project Name").find_next("td").text.strip()
            promoter_name = project_page.find("td", string="Company Name").find_next("td").text.strip()
            promoter_address = project_page.find("td", string="Registered Office Address").find_next("td").text.strip()
            gst_no = project_page.find("td", string="GST No.").find_next("td").text.strip()

            # Save the project information into the CSV file
            writer.writerow([rera_no, project_name, promoter_name, promoter_address, gst_no])

        except AttributeError:
            # If something is missing on the page, show a message
            print("Some details are missing for this project:", project_url)