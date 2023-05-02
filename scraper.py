import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urldefrag
from utils.dbconnect import Sqlite_db
import numpy as np
from numpy.linalg import norm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from english_words import get_english_words_set
from collections import Counter

# extract link
# is valid
# -------------
# It is important to filter out urls that are not with ics.uci.edu domain.
# Detect and avoid crawling very large files, especially if they have low information value
#  is_valid filters a large number of such extensions, but there may be more

mydb = Sqlite_db()
global web2lowerset
web2lowerset = get_english_words_set(['web2'], lower=True)
web2lowerset = np.array(list(web2lowerset))

#check if more than 90% of words in page are in web2 dictionary
def is_words_in_page_valid(words):
    y =  np.isin(np.char.lower(words), web2lowerset)
    if np.mean(y) > 0.9:
        return True
    return False

#average is 15%
#10% will ensure 75% of websites are scraped
# Crawl all pages with high textual information content


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
   
    if mydb.check_visited_url(url):
        return []

    # Parse the HTML content of the webpage using Beautiful Soup
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    page_text = soup.get_text().strip()
    words = page_text.split()
    num_words = len(words)

    if not is_resp_valid(resp, page_text):
        return []

    mydb.add_url(url, page_text, num_words)
    words_counter = Counter(np.char.lower(words))

    for word in words_counter:
        mydb.add_word_count(word, words_counter[word])

    # Extract all of the links on the webpage
    links = []
    for link in soup.find_all('a'):
        href = remove_fragment(link['href'])
        parse = urlparse(url)
        link_signal = True

        # Crawl all pages with high textual information content

        #check if mailto
        if href and ("mailto")in href:
            continue

        #check if absolute url

        if href and (href.startswith("http")):
            pass
        elif href.startswith("www."):
            href = parse.scheme+'://'+href
        elif href.startswith("/www."):
            href = parse.scheme+':/'+href
        elif href.startswith("//www."):
            href = parse.scheme+":"+href
        #check if relative
        elif href and not (href.startswith('http') or ('www')in href):
            # print("---------- url", url,"href",href,"Bombo", url + href)
            href = url + href
        else:
            link_signal = False

        # updates the longest page if needed based on word count
        # check if all whitespace is gone
        # "A word is a basic element of language that carries an objective or practical meaning, can be used on its own, and is uninterruptible" - Wikipedia
        if link_signal:
            links.append(href)

    return links

def is_resp_valid(resp, page_text):
    # checks if response meets constraints
    if resp.status !=200:
        return False

    # Detect and avoid dead URLs that return a 200 status but no data (click here to see what the different HTTP status codes meanLinks to an external site.)
    # Detect and avoid sets of similar pages with no information
    if page_text == None:
        return False
    if page_text == "":
        return False
    
    # Detect and avoid crawling very large files, especially if they have low information value
    textual_content_ratio = len(page_text) / len(resp.raw_response.content)
    if(textual_content_ratio < 0.1):
        return False

    # Detect and avoid crawling very large files, especially if they have low information value
    # FIVE MEGABYTE
    content_length = len(page_text)
    # 5mb
    if int(content_length) > 1024*1024*5000:
        return False
    
    # Detect and avoid infinite traps (e.g., Calendar)
    if(mydb.content_exist(page_text)):
        return False
    
    return True

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    
    
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if not( "cs.uci.edu" in url or "informatics.uci.edu" in url or "stat.uci.edu" in url or "ics.uci.edu" in url):
            return False
    
        # #whitelist
        # return re.match(

        #     # html, txt, json(?)
        #     r"|html|txt|json"
        #     , parsed.path.lower()
        # ) and url not in visited
    
    #blacklist
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def remove_fragment(url):
    pure_url, frag = urldefrag(url)
    return pure_url 