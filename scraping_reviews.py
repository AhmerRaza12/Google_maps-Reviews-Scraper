import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
data = pd.read_excel("Data.xlsx")
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--maximized')
options.add_argument("--disable-blink-features=AutomationControlled")  
options.add_experimental_option("prefs", {"profile.default_content_setting_values.geolocation": 2}) 
driver = webdriver.Chrome(options=options)


def loading_all_reviews():
   
    main_panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[3]'
    try:
        scrollable_div = driver.find_element(By.XPATH, main_panel_xpath)
    except NoSuchElementException:
        
        alternative_panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]'
        scrollable_div = driver.find_element(By.XPATH, alternative_panel_xpath)
    
    prev_scroll_height = driver.execute_script('return arguments[0].scrollTop', scrollable_div)

    for _ in range(11):
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(3)
        curr_scroll_height = driver.execute_script('return arguments[0].scrollTop', scrollable_div)
        if curr_scroll_height == prev_scroll_height:
            break
        prev_scroll_height = curr_scroll_height
        


def appendProduct(file_path2, data):
    temp_file = 'temp_file.csv'
    if os.path.isfile(file_path2):
        df = pd.read_csv(file_path2, encoding='utf-8')
    else:
        df = pd.DataFrame()

    df_new_row = pd.DataFrame([data])
    df = pd.concat([df, df_new_row], ignore_index=True)

    try:
        df.to_csv(temp_file, index=False, encoding='utf-8')
    except Exception as e:
        print(f"An error occurred while saving the temporary file: {str(e)}")
        return False

    try:
        os.replace(temp_file, file_path2)
    except Exception as e:
        print(f"An error occurred while replacing the original file: {str(e)}")
        return False

    return True

def extract_reviews():
    processed_shops = set()  
    if os.path.isfile('processed_shops.txt'):
        with open('processed_shops.txt', 'r') as file:
            processed_shops = set(file.read().splitlines())

    for index, row in data.iterrows():
        shop_name = row['Shop Name']
        shop_id = row['Shop ID']
        latitude = int(row['Lat'])
        longitude = int(row['Lon'])
        num_reviews = row['No. Of Reviews']
        category= str(row['Category'])
        address= row['Address']

        if shop_id in processed_shops or pd.isna(num_reviews):
            continue
        
        address_parts = address.split(", ")
        formatted_address = ", ".join(address_parts[1:])
        formatted_address = formatted_address.replace(' ', '+')
        formatted_shop_name = shop_name.replace(' ', '+')
        wait_time = 10
        search_url = f"https://www.google.com/maps/search/cannabis+store+{formatted_address}"
        driver.get(search_url)
        time.sleep(6)
        

        try:
            link_elements = driver.find_elements(By.XPATH, "//a[@class='hfpxzc']")
            if link_elements:
                link_elements[0].click()
                time.sleep(5)
                reviews_button = WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//button[.='Reviews']")))
                # reviews_button = driver.find_element(By.XPATH, "//button[.='Reviews']")
                reviews_button.click()
                time.sleep(5)
                loading_all_reviews()
            else:
                reviews_button = WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//button[.='Reviews']")))
                # reviews_button = driver.find_element(By.XPATH, "//button[.='Reviews']")
                if reviews_button:
                    reviews_button.click()
                    time.sleep(6)
                    loading_all_reviews()
            
            reviewer_names = driver.find_elements(By.XPATH, "//div[@class='d4r55 ']")
            reviewer_stars = driver.find_elements(By.XPATH, "//span[@class='kvMYJc']")
            reviewer_dates = driver.find_elements(By.XPATH, "//span[@class='rsqaWe']")
            reviewer_reviews = driver.find_elements(By.XPATH, "//span[@class='wiI7pd']")
            for i in range(len(reviewer_names)):
                reviewer_name = reviewer_names[i].text if i < len(reviewer_names) else ''
                reviewer_star = reviewer_stars[i].get_attribute('aria-label') if i < len(reviewer_stars) else ''
                reviewer_date = reviewer_dates[i].text if i < len(reviewer_dates) else ''
                if i < len(reviewer_reviews):
                    more_buttons = driver.find_elements(By.XPATH, f"//button[.='More']")
                    for more_button in more_buttons:
                        more_button.click()
                        time.sleep(1)
                    review_text = reviewer_reviews[i].text
                else:
                    review_text = ''
           
                review = {
                    'Shop Name': shop_name,
                    'Shop ID': shop_id,
                    'Reviewer Name': reviewer_name,
                    'Reviewer Star': reviewer_star,
                    'Reviewer Date': reviewer_date,
                    'Reviewer Review': review_text
                }
                
                
                if not appendProduct('reviews_3.csv', review):
                    print("Error occurred while appending review data.")
                    
               
        except Exception as e:
            print(shop_id+" not scrapped")
            print(f"Error occurred while extracting reviews for '{shop_name}':{shop_id}")
            
        print(shop_id+" scrapped") 
        processed_shops.add(shop_id)

        with open('processed_shops.txt', 'w') as file:
            file.write('\n'.join(processed_shops))

extract_reviews()
driver.quit()
