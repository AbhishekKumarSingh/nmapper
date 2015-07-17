#!/usr/bin/python
import redis
import unicodedata
from google import search, get_page
from bs4 import BeautifulSoup
from termcolor import colored
from helper import extract_domainname, get_company_website


class GSCompanyLookup(object):
    '''This class uses google search api to
       find the company domain.
    '''
    def __init__(self):
        self.rserver = redis.Redis('localhost')

    def get_company_domain(self, searchKey):
        '''looks for the company website from the top five
           url return by google search. If company website
           is found then it parses the url to get domain name
        '''
        search_result = search(searchKey, stop=5)

        for url in search_result:
            keywords = searchKey.split(" ")

            print keywords
            if keywords[0] in url.lower():
                # if links is wikipedia link then parse the webpage to get
                # company homepage
                if "en.wikipedia.org" in url:
                    chomepage = get_company_website(url)
                    if chomepage is not None:
                        return extract_domainname(chomepage)
                return extract_domainname(url)

            try:
                htmlpage = get_page(url)
                soup = BeautifulSoup(htmlpage)

                title = soup.title.text.lower()

                if keywords[0] in title:
                    return extract_domainname(url)
            except:
                print searchKey.ljust(52) + ": Can't parse web page at " + colored(url.ljust(100), 'blue')

    def store_company_domain(self):
        '''reads company name from the redis hash table and
           search googles to find out its domain name. Finally
           stores the result in hash table named GoogleResultFound
        '''
        for cname in self.rserver.hkeys('companyinfo'):
            if self.rserver.hexists('GoogleResultFound', cname):
                continue
            domain = self.get_company_domain(cname)
            if domain is not None:
                self.rserver.hsetnx('GoogleResultFound', cname, domain)
                print cname.ljust(52) + " ----> ".ljust(8) + colored(domain.ljust(100), 'blue')
            else:
                self.rserver.hsetnx('GoogleResultNotFound', cname, domain)
                print cname.ljust(52) + " : Website link not found"

        self.rserver.shutdown()



if __name__=='__main__':
    gs_cl = GSCompanyLookup()

    print '==========================Looking for company domains================================='
    gs_cl.store_company_domain()
    print '==========================process finished============================================'
