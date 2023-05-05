import sqlite3
import numpy as np
from numpy.linalg import norm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Sqlite_db:
    def __init__(self):
        self.con = sqlite3.connect("mydb.db", check_same_thread=False)
        self.cur = self.con.cursor()

#data editorial functions

    #delete all existing tables
    def reset_db(self):
        self.cur.execute("DROP TABLE IF EXISTS visited")
        self.cur.execute("DROP TABLE IF EXISTS word_count")
        self.cur.execute("DROP TABLE IF EXISTS subdomains")
        self.cur.execute("DROP TABLE IF EXISTS blacklist")
        self.cur.execute("CREATE TABLE IF NOT EXISTS subdomains (subdomain TEXT PRIMARY KEY, count INTEGER)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS word_count (word TEXT PRIMARY KEY, count INTEGER)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS visited (url TEXT PRIMARY KEY, text TEXT, num_words INTEGER)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS blacklist (url TEXT PRIMARY KEY)")
        self.con.commit()

    #add a url to the database unique table visited, create new if not exists
    #columns are url, text, and num_words
    #ignore if url already exists
    def add_url(self, url, text, num_words):
        self.cur.execute("INSERT OR IGNORE INTO visited VALUES (?, ?, ?)", (url, text, num_words))
        self.con.commit()

    #add a count to word in the database unique table word_count, create new if not exists
    #columns are word and count
    def add_word_count(self, word, count):
        self.cur.execute("SELECT * FROM word_count WHERE word=? LIMIT 1", (word,))
        if self.cur.fetchone() is None:
            self.cur.execute("INSERT INTO word_count VALUES (?, ?)", (word, count))
        else:
            self.cur.execute("UPDATE word_count SET count=count+? WHERE word=?", (count, word))
        self.con.commit()

    #add subdomain and count to database
    def add_subdomain(self, subdomain):
        self.cur.execute("SELECT * FROM subdomains WHERE subdomain=?", (subdomain,))
        if self.cur.fetchone() is None:
            self.cur.execute("INSERT INTO subdomains VALUES (?, 1)", (subdomain,))
        else:
            self.cur.execute("UPDATE subdomains SET count=count+1 WHERE subdomain=?", (subdomain,))
        self.con.commit()

    #blacklist a url that generats same content with a different url
    def add_blacklist_url(self, url):
        url = '/'.join(url.split("/")[:-1])
        self.cur.execute("INSERT OR IGNORE INTO blacklist VALUES (?)", (url,))
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

    #check if url is in the database, select top one
    def check_visited_url(self, url):
        self.cur.execute("SELECT * FROM visited WHERE url=? LIMIT 1", (url,))
        if self.cur.fetchone() is None:
            return False
        else:
            return True

    #check if similar content is in the database using cosine similarity
    def content_exist(self, content):
        self.cur.execute("SELECT text FROM visited")
        contents = self.cur.fetchall()
        if len(contents) == 0:
            return False
        
        contents = [c[0] for c in contents]
        contents.append(content)
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(contents)
        similarity = cosine_similarity(vectors[-1], vectors[:-1])
        if np.amax(similarity) > 0.8:
            return True
        else:
            return False
    
    #count number of subdomains of ics.uci.edu from database, and print sumber of subdomains of each subdomain
    def count_subdomains(self):
        self.cur.execute("SELECT * FROM visited WHERE url LIKE '%.ics.uci.edu%'")
        ics_urls = self.cur.fetchall()
        subdomains = {}
        for url in ics_urls:
            subdomain = url[0].split("/")[2]
            if subdomain not in subdomains:
                subdomains[subdomain] = 1
            else:
                subdomains[subdomain] += 1
        #print subdomains and their counts
        for subdomain in subdomains:
            print(subdomain, subdomains[subdomain])

        return subdomains
    
    #check if url is generated from blacklisted url
    def is_blacklisted_url(self, url):
        url = '/'.join(url.split("/")[:-1])
        self.cur.execute("SELECT * FROM blacklist WHERE url=? LIMIT 1", (url,))
        if self.cur.fetchone() is None:
            return False
        else:
            return True
