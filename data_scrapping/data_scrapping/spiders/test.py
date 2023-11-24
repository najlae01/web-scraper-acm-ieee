from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as BS
import json
import time
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

data_final = []

def get_data(driver):
    try:
        i = 0
        soup = BS(driver.page_source, 'html.parser')
        my_li = soup.find_all("li", {"class": "ResultItem col-xs-24 push-m"})

        for li in my_li:
            try:
                print(i)
                i += 1
                data_auth = []
                a = li.find("a", {"class": "anchor result-list-title-link u-font-serif text-s anchor-default"})
                link = "https://www.sciencedirect.com" + a['href']
                print(link)

                chrome_options = Options()
                chrome_options.add_argument("--headless")

                with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options) as driver2:
                    driver2.get(link)
                    time.sleep(6)
                    sp = BS(driver2.page_source, 'html.parser')
                    titre = sp.find("h1", {"class": "Head u-font-serif u-h2 u-margin-s-ver"}).get_text()
                    print("Titre: ")
                    print(titre)

                    try:
                        citation = driver2.find_element(By.XPATH,
                                                         "//div[@class='pps-col plx-socialMedia']//span[@class='pps-count']").text
                    except:
                        citation = "0"
                    try:
                        downloads = driver2.find_element(By.XPATH,
                                                          "//div[@class='pps-col plx-capture']//span[@class='pps-count']").text
                    except:
                        downloads = "0"

                    authors = driver2.find_elements(By.XPATH,
                                                    "//button[@class='button-link author size-m workspace-trigger']")
                    for author in authors:
                        author.click()
                        time.sleep(3)
                        name = author.find_element(By.XPATH, "//div[@class='author u-h4']").text
                        print(name)
                        loc = author.find_element(By.XPATH, "//div[@class='affiliation']").text
                        print(loc)
                        data_auth.append({
                            "name": name,
                            "location": loc
                        })

                    date = sp.find("div", {"class": "text-xs"}).get_text()
                    data_final.append({
                        'titre': titre,
                        'date': date,
                        "downloads": downloads,
                        "citations": citation,
                        "authors": data_auth,
                        "article_link": link
                    })
            except Exception as e:
                print(f"Error in processing: {str(e)}")

    except Exception as e:
        print(f"Error: {str(e)}")

chrome_options = Options()
chrome_options.add_argument("--headless")

for i in range(3, 10):
    with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options) as driver:
        driver.get("https://www.sciencedirect.com/search?qs=blockchain&articleTypes=FLA&show=100&offset=" + str(i * 100))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ResultItem")))
        get_data(driver)

# Save data after the loop
with open("newDataFromSc.json", "w") as outfile:
    json.dump(data_final, outfile, indent=2)