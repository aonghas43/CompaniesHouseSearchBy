# progam to do advanced search against Companies House public APIs
import csv
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any

@dataclass 
class SearchResult:
    company_name: str = ''
    company_number: str = ''
    # etc

class SearchBy:
    company_sic_codes = []
    incorporated_from = ''
    incorpoarate_to = ''
    officer_names = []
    api_key_name = ''
    api_key_value = '' 
    def __init__(self, ):
        return

    def read_params(self,params="params.json", api="api.json"):
        # read from params.json
        # read key from api.json
        with open(params, 'r', newline='', encoding='utf-8') as params:
            pass
        with open(api, 'r', newline='', encoding='utf-8') as api:
            pass
        pass

    def search_first_pass(self) ->list: 
        #GET https://api.company-information.service.gov.uk/advanced-search/companies
        #company_status
        #incorporated_from
        #incorporated_to
        #sic_codes : to search using multiple values, use a comma delimited list or multiple of the same key
        #size max 5000
        return []
    
    def search_second_pass(self, firest_pass) -> list:
        # for results returned by first pass
        # GET https://api.company-information.service.gov.uk/company/{company_number}/officers
        # filter by names
        return []

    def write_result(self, second_pass, outfile='results.csv') -> None:
        return

    def run(self) ->None:
            self.read_params()
            first_pass = self.search_first_pass()
            second_pass = self.search_second_pass(first_pass)
            self.write_result(second_pass)
            return
