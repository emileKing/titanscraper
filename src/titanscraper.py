import json
import logging
import os
from logging import Logger

import requests
import xmltodict
from bs4 import BeautifulSoup

from .config import *



class TitanScraper():

    __AUTHOR = "Emile DJIDA GONGDEBIYA"
    __VERSION = "0.0.1"

    TARGETS = tuple()
    DOCUMENT_PARSER = ""
    __LOGGER = logging.getLogger("titanscaper")

    def __init__(self, doc_parser='lxml') -> None:
        self.DOCUMENT_PARSER = doc_parser

        #  prepare the log file
        self.logger.setLevel(LOGGING_LEVEL)
        self.logger.addHandler(LOGGING_FILE_HANDLER)
        self.logger.addHandler(LOGGING_STREAM_HANDLER)
        self.logger.info(f"Starting TitanScraper v{self.__VERSION}")

    def __get_raw_resource(self, link:str, timeout=10) -> tuple:
        """Gets the raw html of a given link.
        
        Arguments:
        `link` -- the actual webpage address to get\n
        `timeout` -- time in seconds to wait for the resource

        Return -- (response_status_code:int, html_doc:str|None)
        
        Error -- in case of a timeout or connection error, it returns (0, None)
        """
        try:
            response = requests.get(link, timeout=timeout)
        except requests.Timeout as error:
            self.LOGGER.error("Timeout error")
            return (0, None)
        else:
            return (response.status_code, response.content)

    @property
    def logger(self) -> Logger:
        """Returns the scraper logger"""
        return self.__LOGGER

    def set_logger(self, logger:Logger) -> None:
        """Initializes a new logger file"""
        self.__LOGGER = logger

    
    @staticmethod
    def __preprocess_element(element, preprocessors:list=None): 
        """Go through all given proprocessors and apply each to the element sequentially"""
        if not preprocessors:
            return element
        for processor in preprocessors:
            element = processor(element)
        return element


    @staticmethod
    def __extract_value(element, rule_attribute:str=None):
        """Extract the given attribbute of an element or it's text content"""
        return element.get(rule_attribute) if rule_attribute else str(element.text)


    @staticmethod
    def __postprocess_value(value, processors:list=None):
        """Apply the given postprocessings to an element's value"""
        if not processors:
            return value
        for processor in processors:
            # check if it is a class
            if type(processor) == type(object):
                value = processor(value).get_value()
            #  or an object
            else:
                value = processor.set_value(value).get_value()
        return value

    
    @staticmethod
    def dict_to_json(dict_obj:dict) -> str:
        """Convert a dictionary into a JSON string"""
        return json.dumps(dict_obj, ensure_ascii=False)


    @staticmethod
    def dict_to_datalist(_dict:dict) -> tuple:
        """returns a tuple of values from a dict"""
        return tuple( _dict.values() )


    def __parse_data(self, html_doc:str, rules:tuple) -> dict:
        """Parse a given html document following a given set of rules and return the data"""
        soup = BeautifulSoup(html_doc, self.DOCUMENT_PARSER)
        data = {}
        for rule in rules:
            # get the elements following the selector
            elements = soup.select(rule.get('selector')) 
            if elements:
                item_index = rule.get("index", 0)

                # get the element from the list of elements
                element = elements[item_index]

                # preprocess the data
                element = self.__preprocess_element(element, rule.get("preprocessors"))

                # extract the value or content from the element
                value = self.__extract_value(element, rule.get('attribute'))
                
                # apply data postprocessing
                value = self.__postprocess_value(value, rule.get("postprocessors"))
                # print(value)

                # type casting
                value = rule['type'](value) if rule.get('type') else value

                # for conditional evaluations
                # this adds the value to the final result only if it meets the evaluated conditions
                if rule.get("evaluators"):
                    for evaluator in rule.get('evaluators'):
                        if evaluator.evaluate(value):
                            data[rule.get('name')] = value
                        else:
                            return {}
                else:
                    data[rule.get('name')] = value

        return data


    def scrap(self, targets:list, rules:list) -> list:
        """Scraps a list of target webpages and returns the data.
        
        Arguments:\n
        `targets` -- the target webpages to scrap\n
        `rules` -- list of DOM selector rules to extract the data from.
            The format is as follows 
            [
                {
                    "name": str,
                    "selector": str,
                    "type": int | str | bool | float , ! defualt str | None
                    "default": Any,
                    "attribute": str !if given, it will get the data from the given attribute
                },
                ...
            ]
        """
        results = []
        for target in targets:
            self.logger.debug("Processing " + target)
            response_status , raw_html = self.__get_raw_resource(target)
            if not raw_html:
                pass

            try:
                data = self.__parse_data(raw_html, rules)
                # print(data)
            except Exception as e:
                self.logger.exception(e)
                # raise
            else:
                # those who failed the evaluations (if given) would not be added
                if len(data):
                    data['source'] = target
                    results.append(data)
                self.logger.debug("Scraping successfull")

        return results

    
    def get_links_from_page(self, target:str, page:str, rule:str='') -> list:
        """Get all links in a given page if no rule is passed, else based on the css selector"""
        _, raw_html = self.__get_raw_resource(target+page)
        soup = BeautifulSoup(raw_html, self.DOCUMENT_PARSER)
        if rule:
            return [ target + link.get('href') for link in soup.select(f'{rule}') ] 
        else:
            return [ target + link.get('href') for link in soup.select('a') ] 


    def xml_to_dict(self, xml_doc:str) -> dict:
        """Takes a string of valid XML and returns a Json of the document tree"""
        return json.loads( json.dumps( xmltodict.parse(xml_doc) ) )


    def load_resource(self, resource:str, timeout:int=10) -> tuple:
        """Gets an online resource and returns the status and content of the resource. 
        Avoid downloading images with this. Use the `download_asset` method instead."""
        return self.__get_raw_resource(resource, timeout=timeout)


    def download_asset(self, asset_url:str, save_to:str=None, overwrite_file:bool=False) -> tuple:
        """Downloads a given asset and returns the data with the response status.
        If an argument for `save_to` is provided, then it will save it at the given location."""
        return ()

    def apply_postprocessing(self, value:str, postprocessors:tuple) -> str:
        return self.__postprocess_value(value, postprocessors)

    def extract_text(self, markup:str, selector:str=None) -> str:
        soup = BeautifulSoup(markup, self.DOCUMENT_PARSER)
        if selector:
            items = soup.select(selector)
            return " ".join([item.text for item in items])
        else:
            return str(soup.text)