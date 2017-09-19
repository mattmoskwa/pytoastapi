import requests
import json
from datetime import datetime
import dateutil.parser
import os


TOKEN_FN = "toast-token.txt"
AUTH_ENDPOINT = "usermgmt/v1/oauth/token"
ORDERS_ENDPOINT = "orders/v2/orders/"
LABOR_ENDPOINT = "labor/v1/"
EMPLOYEES_ENDPOINT = "employees/"
JOBS_ENDPOINT = "jobs/"


class PyToast(object):
    
    def __init__(self, client_id, secret, rguid=None, sandbox=False):
        
        self.client_id = client_id
        self.secret = secret

               
        if rguid is not None:
            self.rguid = None
        else: 
            self.rguid = rguid

        if sandbox == True:
            self.base_url = "https://ws-sandbox-api.eng.toasttab.com/" 
        else:
            self.base_url = "https://ws-api.toasttab.com/"
        
        self.auth_url = self.base_url + AUTH_ENDPOINT

        self.auth_headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }   

        self.data = [
            ('grant_type', 'client_credentials'),
            ('client_id', self.client_id),
            ('client_secret', self.secret),
        ]


        try:
            with open(TOKEN_FN,'r') as f:
                self.auth_token = f.readline()

        except IOError:
            self.auth_token = self.create_auth_token(self.auth_url, self.data, self.auth_headers)
            
            with open(TOKEN_FN, 'w') as f: 
                f.write(self.auth_token) 

                                            
        self.headers = {
            'Toast-Restaurant-External-ID': self.rguid,
            'Authorization': 'Bearer {}'.format(self.auth_token),
            'Content-Type': "application/json"
        }
       


    def get_order(self, o_guid, rguid=None):
        
        ''' Returns a JSON object containing all data relating to a specific order. '''

        endpoint = self.base_url + ORDERS_ENDPOINT + o_guid
        
        if rguid is not None: self.headers['Toast-Restaurant-External-ID'] = rguid
        
        r = requests.get(endpoint, headers=self.headers)     
        
        if self.auth_expired(json.loads(r.content)) == True:
            
            self.headers['Authorization'] = 'Bearer {}'.format(self.create_auth_token(self.auth_url, self.data, self.headers))
            
            r = requests.get(endpoint, headers=self.headers)
        
        
        return json.loads(r.content)



    def get_multiple_orders(self, start_date, end_date, rguid=None):
        
        ''' Returns a JSON object containing all data relating to multiple orders sent within a specified time period. '''
        
        iso_start_date =  dateutil.parser.parse(start_date).isoformat() + ".000-0400"
        iso_end_date =   dateutil.parser.parse(end_date).isoformat() + ".000-0400"

        endpoint = self.base_url + ORDERS_ENDPOINT + "?startDate={}&endDate={}".format(iso_start_date, iso_end_date)

        if rguid is not None: self.headers['Toast-Restaurant-External-ID'] = rguid
        
        r = requests.get(endpoint, headers=self.headers)
        
        if self.auth_expired(json.loads(r.content)) == True:
                
            self.headers['Authorization'] = 'Bearer {}'.format(self.create_auth_token(self.auth_url, self.data, self.headers))
            
            r = requests.get(endpoint, headers=self.headers)

    
        return json.loads(r.content)



    def get_orders_by_day(self, date, rguid=None):
    
        endpoint = self.base_url + ORDERS_ENDPOINT + "?businessDate={}".format(date)
    
        if rguid is not None: self.headers['Toast-Restaurant-External-ID'] = rguid

        r = requests.get(endpoint, headers=self.headers)
        
        if self.auth_expired(json.loads(r.content)) == True:
                
            self.headers['Authorization'] = 'Bearer {}'.format(self.create_auth_token(self.auth_url, self.data, self.headers))
            
            r = requests.get(endpoint, headers=self.headers)
        
        return json.loads(r.content)



    def get_jobs(self, rguid=None):
        
        endpoint = self.base_url + JOBS_ENDPOINT
    
        if rguid is not None: self.headers['Toast-Restaurant-External-ID'] = rguid

        r = requests.get(endpoint, headers=self.headers)
       
        if self.auth_expired(json.loads(r.content)) == True:
                
            self.headers['Authorization'] = 'Bearer {}'.format(self.create_auth_token(self.auth_url, self.data, self.headers))
            
            r = requests.get(endpoint, headers=self.headers)
        
        return json.loads(r.content)



    def get_employee(self, eguid, rguid=None):
            
        endpoint = self.base_url + LABOR_ENDPOINT + "employee/" + eguid

        if rguid is not None: self.headers['Toast-Restaurant-External-ID'] = rguid

        r = requests.get(endpoint, headers=self.headers)
        
        if self.auth_expired(json.loads(r.content)) == True:
                
            self.headers['Authorization'] = 'Bearer {}'.format(self.create_auth_token(self.auth_url, self.data, self.headers))
            
            r = requests.get(endpoint, headers=self.headers)
        
        return json.loads(r.content)



    def get_employees(self, rguid=None):
        
        ''' Returns a list of JSON objects representing data for all employees for a specific restaurant. '''
            
        endpoint = self.base_url + LABOR_ENDPOINT + EMPLOYEES_ENDPOINT

        if rguid is not None: self.headers['Toast-Restaurant-External-ID'] = rguid

        r = requests.get(endpoint, headers=self.headers)
        
        if self.auth_expired(json.loads(r.content)) == True:
                
            self.headers['Authorization'] = 'Bearer {}'.format(self.create_auth_token(self.auth_url, self.data, self.headers))
            
            r = requests.get(endpoint, headers=self.headers)
        
        return json.loads(r.content)



    def create_auth_token(self, url, data, headers):
        
        auth_token = json.loads(requests.post(url, data, headers).content)["access_token"]
        
        return auth_token



    def auth_expired(self, response):
        
        try:
            if response['message'] == 'invalid_token':
                print('Token is expired/invalid. Generating new token ... ')
                return True
            else:
                return False
        
        except KeyError:
            return False
        except TypeError:
            return False



'''     def add_new_employee(self, rguid=None, **kwargs):

        endpoint = self.base_url + EMPLOYEES_ENDPOINT

        data = [ 
            (key,value) for key, value in kwargs.items()
        ]

        if rguid is not None: self.headers['Toast-Restaurant-External-ID'] = rguid
        
        r = requests.get(endpoint, headers=self.headers, data=data)

        return json.loads(r.content) '''


    