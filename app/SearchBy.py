# progam to do advanced search against Companies House public APIs
import csv
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import requests
import re
import time
from typing import Any


@dataclass
class SearchResultCompany:
    company_name: str = ''
    company_number: str = ''
    registered_office: str = ''
    incorporated_on: str = ''
    dissolved_on: str = ''
    officers: str = ''
    # etc


@dataclass
class ParamList:
    company_sic_codes: list = field(default_factory=[].copy)
    incorporated_from: str = ''
    incorporated_to: str = ''
    officer_names: list = field(default_factory=[].copy)


class SearchBy:
    """Input: list of company numbers; output, list filtered to only contin companies with offices with names matching input parameter"""

    def __init__(self, outputdir='C:\\temp'):
        self.outputdir = outputdir
        self.params = ParamList()         # input param list
        self.headers = {}                 # api key
        self.results_companies = []       # outputs
        self.results_officers = []        # outputs
        self.results_companies_csv = []   # csv
        return

    def read_params(self, params="params.json", api="api.json") -> None:
        # read from params.json
        param_list = [attribute for attribute, value in self.params.__dict__.items()]
        with open(params, 'r', newline='', encoding='utf-8') as paramfile:
            data = json.load(paramfile)
            for p in param_list:
                self.params.__setattr__(p, data[p])
            print(self.params)
        # read key from api.json
        with open(api, 'r', newline='', encoding='utf-8') as apifile:
            data = json.load(apifile)
            for a in ["api_key_name", "api_key_value"]:
                self.headers[a] = data[a]
        return

    def write_results(self) -> None:
        with open('companies.json', 'w', encoding='utf-8') as out:
            json.dump(self.results_companies, out)
        with open('officers.json', 'w', encoding='utf-8') as out:
            json.dump(self.results_officers, out)
        return

    def write_records_for_csv(self):
        """flatten company results for CSV output"""
        # output file
        output_dialect = 'excel'    # may need to change to excel_tab if utf8 chars present
        file_suffix = ".csv"        # may need to change to tsv if excel-tab above
        encoding = 'utf-8'
        stamp = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
        outfile = 'SearchResultCompany.csv'
        fn = str.format('{}_{}{}', outfile, stamp, file_suffix)
        out = Path.joinpath(Path(self.outputdir), Path(fn))
        fieldnames = SearchResultCompany().__dict__.keys()
        # write headers
        with out.open('w', newline='', encoding=encoding) as csvfile:
            outwriter = csv.DictWriter(csvfile, dialect=output_dialect,
                                       fieldnames=fieldnames,
                                       quoting=csv.QUOTE_NONNUMERIC)
            outwriter.writeheader()
            # write rows
            outwriter.writerows(self.results_companies_csv)
        return

    def get_company_officers(self, cno) -> Any:
        """get officers for input company number"""
        url = str.format('https://api.company-information.service.gov.uk/company/{}/officers', cno)
        with requests.get(url=url, auth=(self.headers['api_key_value'], ''), allow_redirects=True, timeout=45) as response1:
            data1 = response1.json()
        return data1["items"]

    def get_company_profile(self, cno, officers) -> Any:
        """get company profile for input company number"""
        url = str.format('https://api.company-information.service.gov.uk/company/{}', cno)
        with requests.get(url=url, auth=(self.headers['api_key_value'], ''), allow_redirects=True, timeout=45) as response2:
            data2 = response2.json()
            self.make_company_csv_rec(data2, officers)
            return data2

    def make_company_csv_rec(self, data, officers) -> None:
        """ short CSV record for company"""
        newrec = SearchResultCompany()
        newrec.company_name = data["company_name"]
        newrec.company_number = data["company_number"]
        newrec.incorporated_on = data["date_of_creation"]
        if "date_of_cessation" in data:
            newrec.dissolved_on = data["date_of_cessation"]
        newrec.registered_office = ' '.join(data["registered_office_address"].values())
        ostring = ''
        for o in officers:
            name = o["name"]
            address = ' '.join(o["address"].values())
            if "date_of_birth" in o:
                DOB = ':'.join([str(i) for i in o["date_of_birth"].values()])
            else:
                DOB = ''
            ostring += ':'.join([name, address, DOB])
        newrec.officers = ostring
        # needed to flatten the record suitable for CSV export
        self.results_companies_csv.append(json.loads(json.dumps(newrec.__dict__)))
        return

    def calc_rate_limiting(self, filename):
        """
        Rate limiting applied: 600 requests in 5 minutes
        Calculate if the input will trigger this and apply sleep if so
        """
        with open(filename, 'r') as infile:
            buff = infile.readlines()
            filesize = len(buff)

        if filesize > 500:
            fac = filesize // 500
        else:
            fac = 0
            print("Limiting applied ", fac * 30)
        return fac * 30

    def run_from_txt(self, infilename='Companies-House-search-results.txt') -> None:
        """ read company numbers from list; look for officers matching input string(s)"""
        self.read_params()
        limiter = self.calc_rate_limiting(infilename)
        with open(infilename, 'r') as infile:
            counter = 0
            self.calc_rate_limiting
            for line in infile:
                counter += 1
                cno = line.replace('\n', '')
                if ((counter % 500) == 0) & (limiter > 0):
                    print("sleeping :", limiter)
                    time.sleep(limiter)
                officers = self.get_company_officers(cno)
                found = False
                for i in officers:
                    for r in self.params.officer_names:
                        print(r)
                        if re.search(r, i["name"]):
                            print(i["name"])
                            found = True
                            self.results_officers.append(i)
                            profile = self.get_company_profile(cno, officers)
                            self.results_companies.append(profile)
                            break
                    if found:
                        break
        self.write_results()
        return
