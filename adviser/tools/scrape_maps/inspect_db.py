import pandas as pd
import sqlite3

conn = sqlite3.connect('../../resources/databases/restaurants_stuttgart.db')
db = pd.read_sql('select * from restaurants_stuttgart', conn)
print(db.head)
conn.close()
