import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urldefrag

# extract link
# is valid
# -------------
# It is important to filter out urls that are not with ics.uci.edu domain.
# Detect and avoid crawling very large files, especially if they have low information value
#  is_valid filters a large number of such extensions, but there may be more

#global variables
visited = set()
unique_pages = 0
longest_page = ""
longest_page_length = 0
word_map = {}
subdomains = {}

def sort_word_map():
    # sort word map by value
    sorted_word_map = sorted(word_map.items(), key=lambda x: x[1], reverse=True)
    return sorted_word_map[0:50]

def print_subdomains():
    for subdomain, count in subdomains.items():
        print(subdomain + " " + str(count))

def check_longest(soup, href):
    #checks whitespace in url
    words = soup.get_text().strip().split()
    num_words = len(soup.get_text().strip().split())
    #updates longest
    if num_words > longest_page_length:
        longest_page_length = num_words
        longest_page = href

    for word in words:
        if word in word_map:
            word_map[word] += 1
        else:
            word_map[word] = 1


    #checks subdomains for proper format
    if "ics.uci.edu" in href:
        index = href.index('://')
        if href[index+3:index+7] == "www.":
            href = href[0:index+3] + href[index+7:]
            domain_index = href.index('ics.uci.edu')
            subdomain = href[0:domain_index-1]
        else:
            domain_index = href.index('ics.uci.edu')
            subdomain = href[0:domain_index-1]
        if subdomain in subdomains:
            subdomains[subdomain] += 1
        else:
            subdomains[subdomain] = 1

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

#checks the ratio of the information to file size
def ratio_info(soup):
    # Crawl all pages with high textual information content
    # information to size ratio ( arbitrary )
    textual_content_ratio = sum(map(str.isalpha, soup.get_text())) / len(soup)
    return textual_content_ratio > 0.2

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


    if not is_resp_valid(resp):
        return []
    



    # Parse the HTML content of the webpage using Beautiful Soup
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

    # Extract the title of the webpage
    # title = soup.title.string

    # Extract all of the links on the webpage
    links = []
    for link in soup.find_all('a'):
        href = remove_fragment(link.get('href'))
        
        #check if visited
        if href in visited:
            continue
        
        #check if ratio is good
        if ratio_info(soup):
            continue

        #check if mailto
        if ("mailto")in href:
            continue

        #check if absolute url
        if href and (href.startswith('http') or href.startswith('www')):
            links.append(href)
            visited.add(href)
            unique_pages += 1

        #check if relative
        elif href and not (href.startswith('http') or ('www')in href):
            links.append(url + href)
            unique_pages += 1

        # updates the longest page if needed based on word count
        # check if all whitespace is gone
        # "A word is a basic element of language that carries an objective or practical meaning, can be used on its own, and is uninterruptible" - Wikipedia
        check_longest(soup, href)
        

        

    #print("\n"+resp.url + "   " + url+"\n\n")

            
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
    

    # Detect and avoid crawling very large files, especially if they have low information value
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
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()) and url not in visited

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def remove_fragment(url):
    pure_url, frag = urldefrag(url)
    return pure_url 