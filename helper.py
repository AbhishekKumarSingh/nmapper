import sys
import urllib
import urlparse
from bs4 import BeautifulSoup


def get_soup(url):
    '''return soup from BeautifulSoup operation
       exits the program on no html response
    '''
    try:
        htmlfile = urllib.urlopen(url)
        soup = BeautifulSoup(htmlfile, "html.parser")
        return soup
    except IOError:
        sys.exit("Connection can't be established. Please check your net connection")

def extract_domainname(url):
    '''takes a url parses it and returns domain name
    '''
    newurl = urlparse.urlparse(url)
    hostname = newurl.hostname

    if hostname is None:
        return

    domainname = hostname.replace('www.', '')
    return domainname

def get_company_website(wiki_url):
    '''takes official wiki url of a company
       and returns company home page if it exits
       else it returns None
    '''
    soup = get_soup(wiki_url)

    if soup is None:
        return

    table = soup.find('table', {'class': "infobox"})

    if  table is None:
        return
    website_tag = table.find('th', text='Website')
    if website_tag is None:
        return

    url_tag = website_tag.find_next('td').find('a', href=True)

    if url_tag is None:
        return

    return url_tag['href']
