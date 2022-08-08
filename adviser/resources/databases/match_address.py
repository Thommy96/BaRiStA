from unicodedata import name
import pandas as pd
import sqlite3
import json
import frictionless

conn = sqlite3.connect('restaurants_stuttgart_basic.db') 
db = pd.read_sql('select * from restaurants_stuttgart_basic', conn)
name_address_pair = dict(zip(db.name, db.address))
for i in name_address_pair:
    print(i)
with open("name_address_pair.json", "w", encoding='ISO 8859-1') as fp:
    json.dump(name_address_pair,fp) 
conn.close()