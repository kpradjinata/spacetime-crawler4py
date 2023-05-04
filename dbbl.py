import sqlite3
con = sqlite3.connect("mydb.db", check_same_thread=False)
cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS blacklist (url TEXT PRIMARY KEY)")
