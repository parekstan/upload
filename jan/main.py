"""
Run the court scraper.py file in the python environment!

Input 2

1. Enter the index of the court you want the data for
2. Enter the date in the given format mentioned during the input prompt

Output 1 (Output csv is stored in current working directory)

1.COURT_NAME GIVEN_DATE.csv

*Note: If the csv is empty then there is no data for that particular date for the given court

Modifications remaining

1. Proxy needed for range of dates and all courts
2. Chances of getting banned - MODERATE

Please use with caution

"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import date, timedelta, datetime


class mainWebCrawler:
    SEARCH_DATE = None
    COLUMNS = ['Case Number', 'Filed Date', 'Locality', 'Name', 'Status', 'Defense Attorney', 'Address', 'AKA1', 'AKA2', 'Gender', 'Race', 'DOB', 'Charge', 'Code Section', 'Case Type', 'Class', 'Offense Date', 'Arrest Date', 'Complainant', 'Amended Charge', 'Amended Code', 'Amended Case Type',
               'Date', 'Time', 'Result', 'Hearing Type', 'Courtroom', 'Plea', 'Continuance Code', 'Final Disposition', 'Sentence Time', 'Sentence Suspended Time', 'Probation Type', 'Probation Time', 'Probation Starts', 'Operator License Suspension Time', 'Restriction Effective Date',
               'Operator License Restriction Codes', 'Fine', 'Costs', 'Fine/Costs Due', 'Fine/Costs Paid', 'Fine/Costs Paid Date', 'VASAP', 'courtName', 'searchDate']
    COURT_NAMES = []
    COURT_NAME = None

    def __init__(self):
        self.table = pd.DataFrame(columns=self.COLUMNS)
        self.raw = pd.DataFrame(columns=['Search Date', 'Case ID', 'Case ID URL'])
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("useAutomationExtension", False)
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        self.driver.implicitly_wait(10)
        self.product_urls = []

    def get_court_names(self):
        url = 'https://eapps.courts.state.va.us/gdcourts/caseSearch.do'
        self.driver.get(url)
        self.driver.find_element(by=By.XPATH, value="""//input[@name='accept' and @type='submit' and @value='Accept']""").click()
        self.driver.find_element(by=By.XPATH, value="""//img[@id='btndropdown1']""").click()
        court_name_xpath = self.driver.find_elements(by=By.XPATH, value="""(//ul[@role='listbox']/li)""")
        number_of_courts = len(court_name_xpath)
        for i in range(number_of_courts):
            self.COURT_NAMES.append(court_name_xpath[i].get_attribute('innerText'))

    def set_court(self, court_name):
        self.COURT_NAME = court_name
        self.driver.find_element(by=By.XPATH, value="""//input[@name='selectedCourtName']""").send_keys(f"""{self.COURT_NAME}""")
        self.driver.find_element(by=By.XPATH, value="""//input[@name='selectedCourtName']""").send_keys(Keys.TAB)

    def set_date(self, search_date):
        self.SEARCH_DATE = search_date
        try:
            self.driver.find_element(by=By.XPATH, value="//div[@class='trafficcriminaltab']//a[text()='Hearing Date Search']").click()
            self.driver.find_element(by=By.XPATH, value="""//input[@class='hasDatepicker']""").send_keys(self.SEARCH_DATE)
            self.driver.find_element(by=By.XPATH, value="""//input[@class='hasDatepicker']""").send_keys(Keys.ENTER)
        except:
            self.driver.find_element(by=By.XPATH, value="""//input[@name='selectedCourtName']""").send_keys(f"""{self.COURT_NAME}""")
            self.driver.find_element(by=By.XPATH, value="""//input[@name='selectedCourtName']""").send_keys(Keys.TAB)
            time.sleep(2)
            self.driver.find_element(by=By.XPATH, value="//div[@class='trafficcriminaltab']//a[text()='Hearing Date Search']").click()
            self.driver.find_element(by=By.XPATH, value="""//input[@class='hasDatepicker']""").send_keys(self.SEARCH_DATE)
            self.driver.find_element(by=By.XPATH, value="""//input[@class='hasDatepicker']""").send_keys(Keys.ENTER)

    def get_page_data(self):
        do_run = True
        while do_run:
            table = self.driver.find_elements(by=By.XPATH, value="""//table[@class='tableborder']//tr[contains(@class, 'Row')]//a""")
            for row in table:
                case_id = row.get_attribute('innerText').strip()
                case_id_link = row.get_attribute('href')[:-1] + '1'
                self.raw.loc[len(self.raw.index)] = [self.SEARCH_DATE, case_id, case_id_link]
            try:
                self.driver.find_element(by=By.XPATH, value="//input[@name='caseInfoScrollForward']").click()
            except:
                do_run = False

    def get_data_from_xpath(self, xpath, attrib_value):
        try:
            return self.driver.find_element(by=By.XPATH, value=xpath).get_attribute(attrib_value).replace('\xa0', '')
        except Exception as e:
            return ''

    def scrape_pages(self):
        xpaths = list()
        xpaths.append("(//td[contains(text(), 'Number')])/following-sibling::td[1]")  # Case Number
        xpaths.append("(//td[contains(text(), 'Filed')])/following-sibling::td[1]")  # Filed Date
        xpaths.append("(//td[contains(text(), 'Locality')])/following-sibling::td[1]")  # Locality
        xpaths.append("(//td[contains(text(), 'Name')])/following-sibling::td[1]")  # Name
        xpaths.append("(//td[contains(text(), 'Status')])/following-sibling::td[1]")  # Status
        xpaths.append("(//td[contains(text(), 'Defense')])/following-sibling::td[1]")  # Defense Attorney
        xpaths.append("(//td[contains(text(), 'Address')])/following-sibling::td[1]")  # Address
        xpaths.append("(//td[contains(text(), 'AKA1')]/following-sibling::td[1])")  # AKA1
        xpaths.append("(//td[contains(text(), 'AKA2')])/following-sibling::td[1]")  # AKA2
        xpaths.append("(//td[contains(text(), 'Gender')])/following-sibling::td[1]")  # Gender
        xpaths.append("(//td[contains(text(), 'Race')])/following-sibling::td[1]")  # Race
        xpaths.append("(//td[contains(text(), 'DOB')])/following-sibling::td[1]")  # DOB
        xpaths.append("(//td[contains(text(), 'Charge')])/following-sibling::td[1]")  # Charge
        xpaths.append("(//td[contains(text(), 'Section')])/following-sibling::td[1]")  # Code Section
        xpaths.append("(//td[contains(text(), 'Case')])[3]/following-sibling::td[1]")  # Case
        xpaths.append("(//td[contains(text(), 'Class')])/following-sibling::td[1]")  # Class
        xpaths.append("(//td[contains(text(), 'Offense')])/following-sibling::td[1]")  # Offense Date
        xpaths.append("(//td[contains(text(), 'Arrest')])/following-sibling::td[1]")  # Arrest Date
        xpaths.append("(//td[contains(text(), 'Complainant')])/following-sibling::td[1]")  # Complainant
        xpaths.append("(//td[contains(text(), 'Amended')])[1]/following-sibling::td[1]")  # Amended Charge
        xpaths.append("(//td[contains(text(), 'Amended')])[2]/following-sibling::td[1]")  # Amended Code
        xpaths.append("(//td[contains(text(), 'Amended')])[3]/following-sibling::td[1]")  # Amended Case Type
        xpaths.append("((//tr[@id='toggleHearing']//tr[@class='gridrow'])/td)[1]")  # Date
        xpaths.append("((//tr[@id='toggleHearing']//tr[@class='gridrow'])/td)[2]")  # Time
        xpaths.append("((//tr[@id='toggleHearing']//tr[@class='gridrow'])/td)[3]")  # Result
        xpaths.append("((//tr[@id='toggleHearing']//tr[@class='gridrow'])/td)[4]")  # Hearing Type
        xpaths.append("((//tr[@id='toggleHearing']//tr[@class='gridrow'])/td)[5]")  # Courtroom
        xpaths.append("((//tr[@id='toggleHearing']//tr[@class='gridrow'])/td)[6]")  # Plea
        xpaths.append("((//tr[@id='toggleHearing']//tr[@class='gridrow'])/td)[7]")  # Continuance Code
        xpaths.append("(//td[contains(text(), 'Final')])/following-sibling::td[1]")  # Final Disposition
        xpaths.append("(//td[contains(text(), 'Sentence')])[1]/following-sibling::td[1]")  # Sentence Time
        xpaths.append("(//td[contains(text(), 'Sentence')])[2]/following-sibling::td[1]")  # Sentence Suspended Time
        xpaths.append("(//td[contains(text(), 'Probation')])[1]/following-sibling::td[1]")  # Probation Type
        xpaths.append("(//td[contains(text(), 'Probation')])[2]/following-sibling::td[1]")  # Probation Time
        xpaths.append("(//td[contains(text(), 'Probation')])[3]/following-sibling::td[1]")  # Probation Starts
        xpaths.append("(//td[contains(text(), 'Operator')])[1]/following-sibling::td[1]")  # Operator License Suspension Time
        xpaths.append("(//td[contains(text(), 'Restriction Effective')])/following-sibling::td[1]")  # Restriction Effective Date
        xpaths.append("(//td[contains(text(), 'Operator')])[2]/following-sibling::td[1]")  # Operator License Restriction Codes
        xpaths.append("(//td[contains(text(), 'Fine')])[1]/following-sibling::td[1]")  # Fine
        xpaths.append("(//td[contains(text(), 'Costs')])[1]/following-sibling::td[1]")  # Costs
        xpaths.append("(//td[contains(text(), 'Costs')])[2]/following-sibling::td[1]")  # Fine/Costs Due
        xpaths.append("(//td[contains(text(), 'Costs')])[3]/following-sibling::td[1]")  # Fine/Costs Paid
        xpaths.append("(//td[contains(text(), 'Costs')])[4]/following-sibling::td[1]")  # Fine/Costs Paid Date
        xpaths.append("(//td[contains(text(), 'VASAP')])/following-sibling::td[1]")  # VASAP
        xpaths.append("//div[@id='headerCourtName']")  # Court Name

        temp_list = list()  # empty row list to store current page xpath data
        for index in range(len(self.raw.index)):
            search_date, case_id, url = self.raw.iloc[index]
            self.driver.get(url)
            for xpath in xpaths:
                if xpath:
                    te = self.get_data_from_xpath(xpath, 'innerText')
                    temp_list.append(te)
                else:
                    temp_list.append(xpath)
            temp_list.append(str(search_date))

            self.table.loc[len(self.table.index)] = temp_list
            temp_list.clear()

    def save_to_csv(self):
        custom_date = self.SEARCH_DATE.split('/')
        custom_date = "-".join(custom_date)
        self.table.to_csv(f"{self.COURT_NAME} {custom_date}.csv", index=False)


_from = '2021/01/04' #YYYY/MM/DD
_to = '2021/01/31'

s_split = _from.split("/")
e_split = _to.split("/")
s_date = date(int(s_split[0]), int(s_split[1]), int(s_split[2]))
e_date = date(int(e_split[0]), int(e_split[1]), int(e_split[2]))
date_modified = s_date
_list = [s_date]
while date_modified < e_date:
    date_modified += timedelta(days=1)
    _list.append(date_modified)

crawler = mainWebCrawler()
crawler.get_court_names()
for _name in tqdm(crawler.COURT_NAMES):
    if _name:
        crawler.set_court(_name)
        for _date in tqdm(_list):
            _split = str(_date).split('-')
            crawler.set_date(str(_split[1] + "/" + _split[2] + "/" + _split[0]))
            crawler.get_page_data()
            crawler.scrape_pages()
            crawler.save_to_csv()
