import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from utils.tokenizer import tokenize
import urllib.robotparser as robotparser

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

    # if we can't scrape, return empty list
    if resp.status != 200 or is_valid(resp.url) == False:
        return []
    
    # if page is low-information, return empty list
    if not has_sufficient_content(resp):
        return []

    next_links = []
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')
    found_links = soup.find_all('a')
    for link in found_links:
        # print("debug link:", link)
        # extract link
        href = link.get('href')
        absolute_url = urljoin(resp.url, href)
        # absolute_url = absolute_url.replace(fragment="")

        # if new url is valid, add to list
        if is_valid(absolute_url):
            next_links.append(absolute_url)
        else:
            # prints when url isn't considered valid
            print("invalid url, outside of expected domain")
    # debug that prints next links
    print(next_links)
    return next_links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        # check if url is within the 4 specified domains
        if not within_domains(url):
            return False
        
        # check if url is allowed by robots.txt
        if not obeys_robots_rules(url):
            return False
        
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


def within_domains(url):
    allowed = ['ics.uci.edu', 'cs.uci.edu', 'informatics.uci.edu', 'stat.uci.edu']
    hostname = urlparse(url).netloc
    hostname = hostname.removeprefix('www.')
    if hostname not in allowed:
        return False
    return True


def has_sufficient_content(resp, min_words=100, min_ratio=0.02):
    # returns True if the page has enough textual/informational content to be useful
    if resp.raw_response is None or resp.raw_response.content is None:
        return False
    
    content = resp.raw_response.content

    # pages with small byte-size are probably low-information
    # 404 error pages are typically 512 bytes
    if len(content) <= 512:
        return False
    
    # checking visible word count of the page for info as well
    soup = BeautifulSoup(content, 'lxml')

    # remove non-visible / non-informational elements
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # tokenize visible text 
    visible_text = soup.get_text(separator=' ')
    words = tokenize(visible_text)

    # check if number of words and ratio of HTML to text is sufficient
    word_count = len(words)
    ratio = word_count / max(len(content), 1) # max used to prevent division by 0
    return word_count >= min_words and ratio >= min_ratio


def obeys_robots_rules(url):
    parsed = urlparse(url)
    host = parsed.netloc.removeprefix("www.")
    path = parsed.path

    # informatics.uci.edu
    inf_allowed_paths = ["/wp-admin/admin-ajax.php", "/research/labs-centers/", "/research/areas-of-expertise/", 
                         "/research/example-research-projects/", "/research/phd-research/", "/research/past-dissertations/", 
                         "/research/masters-research/", "/research/undergraduate-research/", "/research/gifts-grants/"]
    
    if host.endswith("informatics.uci.edu"):
        if path.startswith("/research"):
            if not any(path.startswith(p) for p in inf_allowed_paths):
                return False
        
        if path.startswith("/wp-admin/") and not path.startswith("/wp-admin/admin-ajax.php"):
            return False

    # stat.uci.edu
    if host.endswith("stat.uci.edu"):
        if path.startswith("/people") or path.startswith("/happening"):
            return False

    # ics.uci.edu
    if host.endswith("ics.uci.edu"):
        if path.startswith("/people") or path.startswith("/happening"):
            return False

    # cs.uci.edu
    if host.endswith("cs.uci.edu"):
        if path.startswith("/people") or path.startswith("/happening"):
            return False

    return True