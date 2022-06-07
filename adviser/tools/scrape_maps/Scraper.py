from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

IMPLICIT_WAIT = 5

class Scraper():
    def __init__(self):
        self.driver = self.create_driver()
        self.root = None
        self.data_dict = {'name': [], 'rating': [], 'num_reviews': [], 'manner': [], 'description': [], 'address': [], 
                        'opening_hours': [], 'website': [], 'phone_number': [], 'reviews': [], 'price': [], 'category': []}

    def create_driver(self, headless=True):
        chrome_options = Options()
        if headless:  # Optional condition to "hide" the browser window
            chrome_options.headless = True

        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options) 
        # Creation of the "driver" that we're using to interact with the browser
        
        driver.implicitly_wait(IMPLICIT_WAIT) 
        # How much time should Selenium wait until an element is able to interact

        return driver

    def scrape_url(self, url:str):
        self.driver.get(url)
        time.sleep(1)
        source = self.driver.page_source
        soup = BeautifulSoup(source, features='lxml')
        # get root node under which all relevant information is placed
        self.root = soup.find_all('div',{"class":"id-content-container"})[0]

        name = self.get_name()
        rating = self.get_rating()
        num_reviews = self.get_num_reviews()
        manner = self.get_manner()
        description = self.get_description()
        address = self.get_address()
        opening_hours = self.get_opening_hours()
        website = self.get_website()
        phone_number = self.get_phone_number()
        reviews = self.get_reviews()
        price = self.get_price()
        category = self.get_category()

        if not name in self.data_dict['name']:
            self.data_dict['name'].append(name)
            self.data_dict['rating'].append(rating)
            self.data_dict['num_reviews'].append(num_reviews)
            self.data_dict['manner'].append(manner)
            self.data_dict['description'].append(description)
            self.data_dict['address'].append(address)
            self.data_dict['opening_hours'].append(opening_hours)
            self.data_dict['website'].append(website)
            self.data_dict['phone_number'].append(phone_number)
            self.data_dict['reviews'].append(reviews)
            self.data_dict['price'].append(price)
            self.data_dict['category'].append(category)

    def get_name(self):
        try:
            name = self.root.find('h1').span.text.strip()
        except:
            name = None
        return name
    
    def get_rating(self):
        try:
            rating = self.root.find('div', {'role': 'button'}).span.text.strip()
        except:
            rating = None
        return rating
    
    def get_num_reviews(self):
        try:
            num_ratings = self.root.find('button', {'class': 'DkEaL'}).text.strip().split('\xa0')[0].split(' ')[0]
        except:
            num_ratings = None
        return num_ratings

    def get_manner(self):
        try:
            manner = self.root.find_all('div', {'class': 'LTs0Rc'})
            manner = [e['aria-label'].strip() for e in manner]
            manner = '\n'.join(manner)
        except:
            manner = None
        return manner
    
    def get_description(self):
        try:
            description = self.root.find('div', {'class': 'WeS02d'}).span.text.strip()
        except:
            description = None
        return description

    def get_address(self):
        try:
            address = self.root.find('button', {'data-item-id': 'address'}).text.strip()
        except:
            address = None
        return address

    def get_opening_hours(self):
        try:
            opening_hours = self.root.find('div', {'class': 't39EBf GUrTXd'})['aria-label'].strip().split(';')
            opening_hours = [e.split('.')[0] for e in opening_hours]
            opening_hours = '\n'.join(opening_hours)
        except:
            opening_hours = None
        return opening_hours

    def get_website(self):
        try:
            website = self.root.find('button', {'data-item-id': 'authority'}).text.strip()
        except:
            website = None
        return website

    def get_phone_number(self):
        try:
            phone_number = self.root.find('button', {'data-tooltip': 'Copy phone number'}).text.strip()
        except:
            phone_number = None
        return phone_number

    def get_reviews(self):
        try:
            reviews_tmp = self.root.find_all('div', {'class': 'tBizfc fontBodyMedium'})
            reviews = []
            for review in reviews_tmp:
                reviews.append(review.text.split('reviewers')[0].strip())
            reviews = '\n'.join(reviews)
        except:
            reviews = None
        return reviews

    def get_price(self):
        try:
            price = self.root.find('span', {'jsan': '0.aria-label'})['aria-label'].strip()
            price = price.split(':')[1].strip()
        except:
            price = None
        return price
    
    def get_category(self):
        try:
            category = self.root.find('button', {'jsaction': 'pane.rating.category'}).text.strip()
        except:
            category = None
        return category
