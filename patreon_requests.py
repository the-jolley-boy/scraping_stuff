import requests
import json
from string import ascii_lowercase as alc
import csv
import time

def patreon(search):
    url = f"https://patreon.com/api/search?q={search}&page%5Bnumber%5D=1"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'application/vnd.api+json',
        'Accept-Encoding': 'utf-8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'www.patreon.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'X-Requested-With': 'XMLHttpRequest',
        'App-Platform': 'web',
        'App-Version': '2023.11.12.01',
    }

    csv_element = ""

    response = requests.get(url=url, headers=headers)

    output = json.loads(response.text)

    # first, gather first page data then get the page for other pages.
    data_list = output['data']
    for element in data_list:
        csv_element = (csv_element + 
                        element['attributes']['creator_name'] + 
                        "," + element['attributes']['creation_name'] + 
                        "," + str(element['attributes']['post_statistics']['total']) + 
                        "," + str(element['attributes']['patron_count']) + 
                        "," + element['attributes']['url'] + "\n")

    page_total = output["meta"]["pages_total"]
    i = 2
    # now the other pages, if any.
    while i <= page_total:
        time.sleep(1)
        url = f"https://patreon.com/api/search?q={search}&page%5Bnumber%5D={i}"
        response = requests.get(url=url, headers=headers)
        output = json.loads(response.text)

        data_list = output['data']
        for element in data_list:
            csv_element = (csv_element + 
                            element['attributes']['creator_name'] + 
                            "," + element['attributes']['creation_name'] + 
                            "," + str(element['attributes']['post_statistics']['total']) + 
                            "," + str(element['attributes']['patron_count']) +
                            "," + element['attributes']['url'] + "\n")

        i = i + 1

    return csv_element

# Scraping purely through their search feature, can be customized however, this is just to pull a random large set, around 20-30k total.
def main():
    mk = open("patreon_requests_data.csv", "w", encoding="utf-8")
    for i in alc:
        for j in alc:
            patreon_list = patreon(i + j)
            print("Search Complete for " + i + j + ", now adding to DB.") 
            mk.write(patreon_list)
    
    mk.close()        

if __name__ == "__main__":
    main()