import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from utils.tokenizer import tokenize, compute_word_frequencies
from itertools import islice

longest_page_url = None
longest_page_word_count = 0
most_common_words = {}

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
    
    soup = BeautifulSoup(resp.raw_response.content, 'lxml')

    # extracting tokens
    readable_text = soup.get_text(separator=' ')
    tokens = tokenize(readable_text)

    # updating statistics
    update_stats(url, tokens)
    write_to_file()
    
    next_links = []

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

def update_stats(url, tokens):
    global longest_page_url, longest_page_word_count, most_common_words
    word_count = len(tokens)

    # update longest page word count
    if word_count > longest_page_word_count:
        longest_page_word_count = word_count
        longest_page_url = url

    # update 50 most common words
    word_freqs = compute_word_frequencies(tokens)
    merge_frequencies(most_common_words, word_freqs)

def merge_frequencies(global_word_freqs, word_freqs):
    for token, count in word_freqs.items():
        if token in global_word_freqs:
            global_word_freqs[token] += count
        else:
            global_word_freqs[token] = count

def write_to_file(file="crawler_statistics.txt"):
    with open(file, "w") as f:
        f.write("Longest page URL: ")
        f.write(f"{longest_page_url} ({longest_page_word_count})\n\n")

        f.write("50 most common words:\n")

        # sort global word frequencies descending
        sorted_freqs = {token : freq for token, freq in sorted(most_common_words.items(), key=lambda item:item[1], reverse=True)}

        for word, freq in islice(sorted_freqs.items(), 50):
            f.write(f"{word}: {freq}\n")

