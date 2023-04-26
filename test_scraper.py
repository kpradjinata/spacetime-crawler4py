#!/usr/bin/env python
# coding: utf-8

# In[7]:


from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler
from scraper import scraper
from utils import get_logger
from utils.download import download


def main(config_file, restart):
#     cparser = ConfigParser()
#     cparser.read(config_file)
#     config = Config(cparser)
#     config.cache_server = get_cache_server(config, restart)
#     crawler = Crawler(config, restart)
#     crawler.start()
    pass

# In[8]:

if __name__ == "__main__":
    #temp url to test scraper on single url
    my_url = "https://www.ics.uci.edu"
    
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", default="config.ini", type=str)
    args = parser.parse_args()
    

    cparser = ConfigParser()
    cparser.read(args.config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, args.restart)

    logger = get_logger(f"Worker-TEST")
    resp = download(my_url, config, logger) # resp argument

    scraper(my_url, resp) #scraper function to test

