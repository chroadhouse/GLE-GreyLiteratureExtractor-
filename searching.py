from googlesearch import search
from datetime import datetime
import urllib3
import certifi
import json
from bs4 import BeautifulSoup


# So we can use this now to generate a new list 

# So queries are: 
# Have these to begin with - can always go back through them
queries = ['Fact Checking AND AI',
           'Fact Checking AND Artificial Intelligence',
           'Fact Checker AND AI',
           'Fact Checker AND Artificial Intelligence',
           'Fact Checking Practitoner AND Artificial Intelligence',
           'Fact Checking Practitoner AND Artifical Intelligence',
           ]



# Running the search method - ti
def run_search(queries):
    temp_data_storage = []
    for q in queries:
        print('Current Query is '+ q)
        temp = list(search(q, num_results=150, lang='en',sleep_interval=30))
        result_date = datetime.now().strftime('%x')
        result_time = datetime.now().strftime('%X')
        for t in temp:
            # URL might not be what i was thinking it is 
            temp_data_storage.append({'URL':t, 'Query':q, 'Date':result_date, 'Time':result_time})
        
    return temp_data_storage


def get_HTML(url):
    try:
        try:
            http = urllib3.PoolManager(
                cert_reqs = 'CERT_REQUIRED',
                ca_certs = certifi.where()
            )
        except:
            http = urllib3.PoolManager(
                cert_reqs = 'CERT_REQUIRED',
                ca_certs = certifi.old_where()
            )
        r = http.request('GET', url=url, timeout=30.0)
        if r.status == 200:
            html = r.data.decode('utf-8')
            return html, True
        else:
            return f'Failed -- Status Code: {str(r.status)}', False
    except Exception as e:
        return '-1 '+str(e), False
    



# Okay so now we have the data we can move on to acc scraping the data 
def scrape_site(data):
    temp_list = []
    passed = False
    id = 0
    for row in data:
        url = row['URL']
        html, passed = get_HTML(url)
        print(html)
        if passed:
            temp_list.append({'ID':id, 'Query':row['Query'], 'URL':row['URL'], 'Date':row['Date'], 'Time':row['Time'], 'HTML':html})
            id +=1 
    return temp_list


# Now we have our HTML data we can go through and try and just pull the specific bits that we need 
def extract_HTML(data):
    temp_list = []
    for row in data:
        # Key is HTML
        soup = BeautifulSoup(row['HTML'], 'html.parser')
        tag_names = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "title", "article", "date"]
        buffer = ""

        for tag in soup.descendants:
            if not hasattr(tag, 'text'):
                continue

            if tag.name in tag_names:
                text = tag.get_text().strip()
                buffer += text +'\n'

        temp_list.append({'ID':row['ID'], 'Query':row['Query'], 'URL':row['URL'], 'Date':row['Date'], 'Time':row['Time'], 'Text':buffer, 'HTML':row['HTML']})
    return temp_list

def remove_duplicates(data):
    # Removes the duplicates 
    temp_list = []
    for row in data:
        check_url = row['URL']
        if check_url not in temp_list:
            temp_list.append(row)

    
    return temp_list
  

def dump_data(data):
    # Dump the dictionary into a json file once we have all the data
    file_path = 'output.json'
    
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=2)

def main():
    print('Commencing Search')
    data = run_search(queries)
    print('Search complete \n Commencing data cleaning')
    clean_data = remove_duplicates(data)
    print('Data cleaning complete \n Commencing Web scraping')
    html_data = scrape_site(clean_data)
    print('Web scraping complete \n Commencing html extraction')
    text_data = extract_HTML(html_data)
    dump_data(text_data)
    print('Data is saved in JSON file')

if __name__ == '__main__':
    main()
   