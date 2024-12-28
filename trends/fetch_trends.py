from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
import datetime

import uuid
import time
from bs4 import BeautifulSoup
print("Starting Selenium Script...")



# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["twitter_trends"]
collection = db["trends"]
counter_collection = db['counters']
end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Selenium setup
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Login credentials
username = "JamesBond398500"
password = "00000786"

try:
    # Navigate to Twitter login page
    driver.get("https://twitter.com/login")

    # Step 1: Enter username or email
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "text")))
    username_field = driver.find_element(By.NAME, "text")
    username_field.send_keys(username)
    username_field.send_keys(Keys.RETURN)


    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "password")))
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    print("herer5")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//a[@data-testid='AppTabBar_Explore_Link']"))
    ).click()

    print("here7")
    driver.get("https://x.com/explore/tabs/trending")
    print("hrerer")
    time.sleep(20)
    print("57758")
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, "html.parser")
    print("654334")

    trends = soup.find_all("div", {"data-testid": "trend"}, limit=5)

    trending_data = []
    for trend in trends:
        try:
            topic_name = trend.find('div',
                                    class_='css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-b88u0q r-1bymd8e')
            if topic_name:
                trending_data.append(topic_name.get_text(strip=True))
        except Exception as e:
            print(f"Error parsing trend: {e}")
            continue
    print("Trending data to be saved:", trending_data)

    # Increment count in counter collection
    counter_collection.update_one(
        {'_id': 'trends_count'},
        {'$inc': {'count': 1}},
        upsert=True
    )
    count_doc = counter_collection.find_one({'_id': 'trends_count'})
    current_count = count_doc['count'] if count_doc else 0
    try:
        collection.insert_one({
            "_id": str(uuid.uuid4()),

            "date_time":end_time,
            "trends": trending_data,
            "ip_address": "127.0.0.1",
            "count": current_count
        })
        print("Data inserted successfully into MongoDB.")
    except Exception as e:
        print("Error inserting data into MongoDB:", e)

    print(trending_data)
except Exception as e:
    print("An error occurred:", e)

finally:
    driver.quit()
