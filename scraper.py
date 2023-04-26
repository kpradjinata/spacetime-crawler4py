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

visited = set()
# word_count = {url: {word: count}}
word_count = dict()


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

        if href and (href.startswith('http') or href.startswith('www')):
            links.append(href)
            visited.add(href)

        if ("mailto")in href:
            continue

        # #check if relative
        elif href and not (href.startswith('http') or ('www')in href):
            links.append(url + href)


    print("\n"+resp.url + "   " + url+"\n\n")

            
    return links

def is_resp_valid(resp):
    # checks if response meets constraints
    if resp.status !=200:
        return false

    # Detect and avoid dead URLs that return a 200 status but no data (click here to see what the different HTTP status codes meanLinks to an external site.)
    # Detect and avoid sets of similar pages with no information
    if resp.raw_response.content == None:
        return false
    if resp.raw_response.content == "":
        return false

    # # Detect and avoid infinite traps with redirections
    # if resp.status in [301, 302, 303, 307, 308]:
    #     if(resp in resp.history):
    #         return false
    #     for hist_content in resp.history:
    #         hist_content = hist_content.raw_response.content
    #         if hist_content == resp.raw_response.content:
    #             return false

    # Detect and avoid crawling very large files, especially if they have low information value
    # ONE MEGABYTE

    # Crawl all pages with high textual information content
    # information to size ratio ( arbitrary )


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