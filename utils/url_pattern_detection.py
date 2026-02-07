from urllib.parse import urlparse, parse_qs

def get_url_parts(url):
    parsed_url = urlparse(url)

    
    domain, path = parsed_url.netloc, parsed_url.path
    query_str = parsed_url.query
    query_str_dict = parse_qs(query_str)

    print(f"Original URL: {url}")
    print(f"Domain (netloc): {domain}")
    print(f"Path: {path}")
    print(f"Raw Query String: {query_str}")
    print(f"Query Strings (dict): {query_str_dict}")

# def process_url_str(url):
    





if __name__=="__main__":
    get_url_parts("https://ics.uci.edu/events/")
    get_url_parts("https://ics.uci.edu/event/master-of-computer-science-information-session-02-09-26/")
    get_url_parts("https://uci.zoom.us/meeting/register/l39e8nu_Qy-CT5pi0VeL_g#/registration")