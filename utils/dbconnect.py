import sqlite3

class Sqlite_db:
    def __init__(self):
        self.con = sqlite3.connect("mydb.db")
        self.cur = self.con.cursor()

#data editorial functions

    #delete all existing tables
    def reset_db(self):
        self.cur.execute("DROP TABLE IF EXISTS visited")
        self.cur.execute("DROP TABLE IF EXISTS word_count")
        self.cur.execute("DROP TABLE IF EXISTS subdomains")
        self.cur.execute("CREATE TABLE IF NOT EXISTS subdomains (subdomain TEXT PRIMARY KEY, count INTEGER)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS word_count (word TEXT PRIMARY KEY, count INTEGER)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS visited (url TEXT PRIMARY KEY, text TEXT, num_words INTEGER)")
        self.con.commit()

    #add a url to the database unique table visited, create new if not exists
    #columns are url, text, and num_words
    #ignore if url already exists
    def add_url(self, url, text, num_words):
        self.cur.execute("INSERT OR IGNORE INTO visited VALUES (?, ?, ?)", (url, text, num_words))
        self.con.commit()

    #add a count to word in the database unique table word_count, create new if not exists
    #columns are word and count
    def add_word_count(self, word):
        self.cur.execute("SELECT * FROM word_count WHERE word=?", (word,))
        if self.cur.fetchone() is None:
            self.cur.execute("INSERT INTO word_count VALUES (?, 1)", (word,))
        else:
            self.cur.execute("UPDATE word_count SET count=count+1 WHERE word=?", (word,))
        self.con.commit()

    #add subdomain and count to database
    def add_subdomain(self, subdomain):
        self.cur.execute("SELECT * FROM subdomains WHERE subdomain=?", (subdomain,))
        if self.cur.fetchone() is None:
            self.cur.execute("INSERT INTO subdomains VALUES (?, 1)", (subdomain,))
        else:
            self.cur.execute("UPDATE subdomains SET count=count+1 WHERE subdomain=?", (subdomain,))
        self.con.commit()
    
#below are report functions

    #get 50 most counted words
    def get_most_counted_word(self):
        self.cur.execute("SELECT * FROM word_count ORDER BY count DESC LIMIT 50")
        return self.cur.fetchall()

    #get url of the longest page
    def get_longest_page(self):
        self.cur.execute("SELECT url FROM visited ORDER BY num_words DESC LIMIT 1")
        return self.cur.fetchone()
    
    #get number of unique pages
    def get_unique_pages(self):
        self.cur.execute("SELECT COUNT(*) FROM visited")
        return self.cur.fetchone()[0]

    #check if url is in the database
    def check_url(self, url):
        self.cur.execute("SELECT * FROM visited WHERE url=?", (url,))
        if self.cur.fetchone() is None:
            return False
        else:
            return True

    #check if content is in the database
    def content_exist(self, content):
        self.cur.execute("SELECT * FROM visited WHERE text=?", (content,))
        if self.cur.fetchone() is None:
            return False
        else:
            return True
    