from seleniumwire import webdriver as selenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pandas as pd
from selenium.common.exceptions import NoSuchElementException

def start_driver(driver_name):
    options = Options()
    match driver_name:
        case 'default':
            options.add_argument("user-data-dir=./user-profile")
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
            options.add_argument(f'user-agent={user_agent}')
            options.add_argument("--window-size=1600,900")
            options.add_argument("--incognito")
            driver = selenium.Chrome(options=options)
    return driver

def login(driver, username, password):
    sleep(3)
    id = driver.find_element(By.ID, 'username')
    id.send_keys(username)
    sleep(2)
    pas = driver.find_element(By.ID, 'password')
    pas.send_keys(password)
    sleep(2)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()

def scrape_data(driver, linkedin_url, scraped_columns):
    sleep(5)
    driver.find_element(By.XPATH, '//a[@aria-current="false"]').click()
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div[2]')))
    sleep(5)
    try:
        all_elements = driver.find_element(By.XPATH, '//*[@class="ember-view"]/section').text.split('\n')
        index = 0
        overview = ''
        industry = ''
        emp_size = ''
        city = ''
        state = ''
        founded = ''
        speciality = ''
        contact_info = ''
        website = ''
        for element in all_elements:
            index += 1
            if element=='Overview':
                overview = all_elements[index]
            elif element=='Website':
                website = all_elements[index]
            elif element=='Phone':
                contact_info = all_elements[index]
            elif element=='Industry':
                industry = all_elements[index]
            elif element=='Company size':
                emp_size = all_elements[index+1] if 'on LinkedIn' in all_elements[index+1] else ''
            elif element=='Headquarters':
                place = all_elements[index]
            elif element=='Specialties':
                speciality = all_elements[index]
            elif element=='Founded':
                founded = all_elements[index]

        try:
            title_element = driver.find_elements(By.XPATH, '//span[@dir="ltr"]')
            company_name = title_element[0].text
        except:
            company_name = ''

        try:
            emp_size = emp_size.split('\n')[0]
        except:
            emp_size = emp_size

        try:
            place = place.split(', ')
            city = place[0]
            state = place[-1]
        except:
            city = city
            state = state

        try:
            funding_element = driver.find_elements(By.CLASS_NAME, 't-light')
            funding = funding_element[0].text 
        except:
            funding = ''

        try:
            locations_element = driver.find_elements(By.XPATH, '//p[@dir="ltr"]')
            locations = locations_element[0].text
        except:
            locations = ''

        # Append the scraped data to the scraped_columns DataFrame
        scraped_columns['LinkedIn URL'].append(linkedin_url)
        scraped_columns['Company Name'].append(company_name)
        scraped_columns['Industry'].append(industry)
        scraped_columns['City'].append(city)
        scraped_columns['State'].append(state)
        scraped_columns['Employee Size'].append(emp_size)
        scraped_columns['Overview'].append(overview)
        scraped_columns['Website'].append(website)
        scraped_columns['Contact Info'].append(contact_info)
        scraped_columns['Funding Info'].append(funding)
        scraped_columns['Founded'].append(founded)
        scraped_columns['Specialties'].append(speciality)
        scraped_columns['Locations'].append(locations)
        
        driver.find_elements(By.XPATH, '//a[@aria-current="false"]')[-1].click()
        sleep(5)
        people = driver.find_elements(By.XPATH, '/html/body/div[5]/div[3]/div/div[2]/div/div[2]/main/div[2]/div/div[2]/div/div[1]/ul/li')
        done = 0
        index = 0
        while done < 20:
            full_name = 'Full Name ' + str(done+1)
            designation = 'Designation ' + str(done+1)
            try:
                scraped_columns[designation].append(people[index].text.split('\n')[1])
                scraped_columns[full_name].append(people[index].text.split('\n')[0])
                done+=1
                index+=1
            except:
                scraped_columns[full_name].append('')
                scraped_columns[designation].append('')
                done+=1
                
        print(f'{company_name} has been scraped.')
        
    except Exception as error:
        print(error)
    
    return scraped_columns

def check_captcha(driver):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'captcha-internal')))
        input('Solve the captcha and press Enter key.')
    except:
        print('No captcha occurs.')

def send_sms(driver):
    try:
        check_captcha(driver)
        text_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'try-another-way')))
        text_button.click()
        print('Sending SMS')
        sleep(2)
    except Exception as error:
        print('Verifying...')

def check_verification(driver):
    try:
        send_sms(driver)
        verfication = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//input[@name="pin"]')))
        code = input('Enter the verification code that has been sent to your account or mobile. - ')
        sleep(2)
        verfication.send_keys(code)
        sleep(2)
        submit_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@type="submit"]')))
        submit_button.click()
        print('You have logged in successfully')
        
    except Exception as error:
        print('You have logged in successfully')

def scraper():
    driver = start_driver('default')
    DOMAIN = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    driver.get(DOMAIN)
    login(driver, username, password)
    check_verification(driver)
    excel_file = 'data.xlsx'
    df = pd.read_excel(excel_file)
    scraped_columns = {
        'LinkedIn URL' : [],
        'Company Name' : [],
        'Industry' : [],
        'City' : [],
        'State' : [],
        'Employee Size' : [],
        'Overview' : [],
        'Website' : [],
        'Contact Info' : [],
        'Funding Info' : [],
        'Founded' : [],
        'Specialties' : [],
        'Locations' : [],
    }
    
    for iter in range(20):
        full_name = 'Full Name ' + str(iter+1)
        designation = 'Designation ' + str(iter+1)
        scraped_columns[full_name] = []
        scraped_columns[designation] = []
    
    for index, row in df.iterrows():
        linkedin_url = row['Linkedin URL']
        driver.get(linkedin_url)
        sleep(5)
        scraped_columns = scrape_data(driver, linkedin_url, scraped_columns)
        sleep(10)
            
    df = pd.DataFrame(scraped_columns)
    df.to_excel('results.xlsx', index=False)
    driver.quit()

if __name__ == "__main__":
    username = input('Enter desired Username - ')
    password = input('Enter Password - ')
    scraper()
