from unicodedata import name
import pandas as pd
import sqlite3
import json
import frictionless

conn = sqlite3.connect('restaurants_stuttgart.db') 
db = pd.read_sql('select * from restaurants_stuttgart', conn)
name_openingtime_pair = dict(zip(db.name, db.opening_hours))
#for i in name_openingtime_pair:
#    print(name_openingtime_pair[i])
with open("name_openingtime_pair.json", "w", encoding='ISO 8859-1') as fp:
    json.dump(name_openingtime_pair,fp) 
conn.close()