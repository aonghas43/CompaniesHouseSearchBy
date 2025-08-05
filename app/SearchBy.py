# progam to do advanced search against Companies House public APIs
import csv
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import requests
import re
from typing import Any

@dataclass 
class SearchResultCompany:
    company_name: str = ''
    company_number: str = ''
    # etc

@dataclass
class ParamList:
    company_sic_codes: list = []
    incorporated_from: str = ''
    incorporated_to: str = ''
    officer_names: list = []

class SearchBy:
 
    api_key_name = ''
    api_key_value = '' 
    results_companies = []
    results_officers = []
    def __init__(self, outputdir='C:\temp'):
        self.outputdir = outputdir
        self.params = ParamList()
        self.headers = {}
        return

    def read_params(self, params="params.json", api="api.json")->None:
        # read from params.json
        # read key from api.json
        param_list = [attribute for attribute, value in self.params.__dict__.items()]
        with open(params, 'r', newline='', encoding='utf-8') as paramfile:
            data = json.load(paramfile)
            for p in param_list:
                self.__setattr__(p, data[p])
            pass
        with open(api, 'r', newline='', encoding='utf-8') as apifile:
            data = json.load(apifile)
            for a in ["api_key_name", "api_key_value"]:
                 self.headers[a] = data[a]
        return

    def search_first_pass(self) ->list: 
        #GET https://api.company-information.service.gov.uk/advanced-search/companies
        #company_status
        #incorporated_from
        #incorporated_to
        #sic_codes : to search using multiple values, use a comma delimited list or multiple of the same key
        #size max 5000
        url = 'https://api.company-information.service.gov.uk/advanced-search/companies'
       
        with requests.get(url=url, auth=(self.headers['api_key_value'],''), allow_redirects=True, timeout=45) as response:
            results = response.json()["items"]
        return results
    
    def search_second_pass(self, first_pass) -> list:
        # for results returned by first pass
        # GET https://api.company-information.service.gov.uk/company/{company_number}/officers
        # requires API authentication 
        # https://developer.company-information.service.gov.uk/authentication
        # filter by names
        results = []
        for el in first_pass:
            cno = el.thing
            url = str.format('https://api.company-information.service.gov.uk/company/{}/officers), cno')
            found = False
            with requests.get(url=url, auth=(self.headers['api_key_value'],''), allow_redirects=True, timeout=45) as response:
                found = False
                # process response, look for match
                # https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/resources/officerlist?v=latest
                data = json.load(response.json())
                for i in data["items"]:
                    for r in self.params.officer_names:
                        if re.search(r,i.name):
                           self.results_companies.append(el)
                           self.results_officers.append(data["items"])
                           found = True
                           break
                    if found:
                        break
                if found:
                    break
            if found:
                break
                         # TODO, make composite result record of company details and officer details
        return results

    def write_results(self) -> None:
        with open('companies.json', 'w', encoding='utf-8') as out:
            json.dump(self.results_companies, out)
        with open('officers.json', 'w', encoding='utf-8') as out:
            json.dump(self.results_officers, out)

    def makeElement(self) ->SearchResultCompany:
        return SearchResultCompany()

    def write_result_csv(self, second_pass, outfile='results.csv') -> None:
        """ file names have timetamp embedded """
        output_dialect = 'excel'
        file_suffix = ".csv"
        encoding='utf-8'
        stamp = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
        fn = str.format('{}_{}{}', outfile, stamp, file_suffix)
        out = Path.joinpath(Path(self.outputdir), Path(fn))

        fieldnames = self.makeElement().__dict__.keys()

        with out.open('w', newline='', encoding=encoding) as csvfile:
            outwriter = csv.DictWriter(csvfile, dialect=output_dialect,
                                       fieldnames=fieldnames,
                                       quoting=csv.QUOTE_NONNUMERIC)
            outwriter.writeheader()
            outwriter.writerows(second_pass)
        return

    def run(self) ->None:
            self.read_params()
            first_pass = self.search_first_pass()
            second_pass = self.search_second_pass(first_pass)
            self.write_results()
            return
