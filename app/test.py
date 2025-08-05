import requests


url1 = 'https://api.company-information.service.gov.uk/advanced-search/companies'

params = {"incorporated_from": '1981-01-01',
"incorporated_to": "1990-01-01",
"sic_codes" : [62011, 62012, 62020,62030,95110]
}

resp1 = requests.get(url=url1, allow_redirects=True, timeout=45, params = params, auth=('a0a7ad08-83b8-4382-b657-b53c633e57fc',''))
thing1 = resp1.json()["items"][0]
print(thing1)

url2='https://api.company-information.service.gov.uk/company/' + thing1.company_number + '/officers'

resp2 = requests.get(url=url2, allow_redirects=True, timeout=45,auth=('a0a7ad08-83b8-4382-b657-b53c633e57fc',''))

print(resp2.json()["items"])