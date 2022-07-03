from Scraper_basic import Scraper
import pandas as pd
import sqlite3
from tqdm import tqdm

urls = []
with open('urls.txt', 'rt') as f:
    for line in f:
        urls.append(line)

scraper = Scraper()

for url in tqdm(urls):
    try:
        scraper.scrape_url(url)
    except:
        print(f'Something went wrong with this url:{url}')
        pass

df = pd.DataFrame.from_dict(scraper.data_dict)

conn = sqlite3.connect('../../resources/databases/restaurants_stuttgart_basic.db')
#print(sqlite3,version)
df.to_sql(name='restaurants_stuttgart_basic', con=conn, if_exists='replace', index=False)

db = pd.read_sql('select * from restaurants_stuttgart_basic', conn)
print(db.head)
conn.close()
