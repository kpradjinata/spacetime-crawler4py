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

# extract link
# is valid
# -------------
# It is important to filter out urls that are not with ics.uci.edu domain.
# Detect and avoid crawling very large files, especially if they have low information value
#  is_valid filters a large number of such extensions, but there may be more
"""
To do:
(+1 points) Implement checks and usage of the robots and sitemap files.

(+2 points) Implement exact and near webpage similarity detection using the methods discussed in the lecture.
 Your implementation must be made from scratch, no libraries are allowed.

(+5 points) Make the crawler multithreaded
However, your multithreaded crawler MUST obey the politeness rule: two or more requests to the same domain, possibly from separate threads,
must have a delay of 500ms (this is more tricky than it seems!).
To do this part of the extra credit, you should read the "Architecture" section of the README.md file.
Basically, to make a multithreaded crawler, you will need to:
    1 Reimplement the Frontier so that it's thread-safe and so that it makes politeness per domain easy to manage
    2 Reimplement the Worker thread so that it's politeness-safe
    3 Set the THREADCOUNT variable in Config.ini to whatever number of threads you want
    4 If your multithreaded crawler is knocking down the server, you may be penalized, so make sure you keep it polite
        (and note that it makes no sense to use a too large number of threads due to the politeness rule that you MUST obey).
"""
mydb = Sqlite_db()
global web2lowerset
web2lowerset = get_english_words_set(['web2'], lower=True)

#check if more than 90% of words in page are valid
def is_words_in_page_valid(words):
    y =  np.isin(words.lower(), web2lowerset)
    if np.mean(y) > 0.9:
        return True
    return False

def sort_word_map():
    # sort word map by value
    sorted_word_map = sorted(word_map.items(), key=lambda x: x[1], reverse=True)
    return sorted_word_map[0:50]

def print_subdomains():
    for subdomain, count in subdomains.items():
        print(subdomain + " " + str(count))

#average is 15%
#10% will ensure 75% of websites are scraped
# Crawl all pages with high textual information content
def ratio_info(resp, soup):
    textual_content_ratio = len(soup.get_text()) / len(resp.raw_response.content)
    return textual_content_ratio > 0.1

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

    # Extract all of the links on the webpage
    links = []
    for link in soup.find_all('a'):
        href = remove_fragment(link.get('href'))
        parse = urlparse(url)
        link_signal = False
        page_text = soup.get_text().strip()

        #check if visited
        if mydb.check_visited_url(href):
            continue

        # Crawl all pages with high textual information content
        # information to size ratio ( arbitrary )
        if not ratio_info(resp, soup):
            continue
        #check if mailto
        if href and ("mailto".encode())in href:
            continue

        #check if absolute url

        if href and (href.startswith("http")):link_signal = True
        elif href.startswith("www."):
            href = parse.scheme+'://'+href
            link_signal = True

        elif href.startswith("/www."):
            href = parse.scheme+':/'+href
            link_signal = True

        elif href.startswith("//www."):
            href = parse.scheme+":"+href
            link_signal = True

        #check if relative
        elif href and not (href.startswith('http') or ('www')in href):
            # print("---------- url", url,"href",href,"Bombo", url + href)
            href = url + href
            link_signal = True
        
        # updates the longest page if needed based on word count
        # check if all whitespace is gone
        # "A word is a basic element of language that carries an objective or practical meaning, can be used on its own, and is uninterruptible" - Wikipedia
        if link_signal:
            words = page_text.split()
            num_words = len(words)
            links.append(href)
            mydb.add_url(href, resp.raw_response.content, num_words)

            for word in words:
                mydb.add_word_count(word)
    #print links with url
    print("url", url, "links", links)

    return links

def is_resp_valid(resp):
    # checks if response meets constraints
    if resp.status !=200:
        return False

    # Detect and avoid dead URLs that return a 200 status but no data (click here to see what the different HTTP status codes meanLinks to an external site.)
    # Detect and avoid sets of similar pages with no information
    if resp.raw_response.content == None:
        return False
    if resp.raw_response.content == "":
        return False

    # # Detect and avoid infinite traps with redirections
    if(resp.status in [301, 302, 303, 307, 308]):
        if(mydb.content_exist(resp.raw_response.content)):
            print("content exist")
            return False

    # Detect and avoid crawling very large files, especially if they have low information value
    # FIVE MEGABYTE
    content_length = int(resp.raw_response.content.headers.get('content-length'))
    # 5mb
    if int(content_length) > 1024*1024*5000:
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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())# and url not in visited

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def remove_fragment(url):
    pure_url, frag = urldefrag(url)
    return pure_url 