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
ISO_TIMEZONE = ".000-0400"


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
        
        # should just be
        # if self.auth_expired(json.loads(r.content))
        # if foo == True is redundant
        if self.auth_expired(json.loads(r.content)) == True:
            
            self.headers['Authorization'] = 'Bearer {}'.format(self.create_auth_token(self.auth_url, self.data, self.headers))
            
            r = requests.get(endpoint, headers=self.headers)
        
        
        return json.loads(r.content)



    def get_multiple_orders(self, start_date, end_date, rguid=None):
        
        ''' Returns a JSON object containing all data relating to multiple orders sent within a specified time period. '''
        
        # It's better to add the timezone while you have a datetime object,
        # rather than stringifying it and adding the ISO code afterwards
        # The rationale here is that it's best to work with code objects for as long as you can,
        # and only turn it into a string when you really need to
        # iso_start_date = dateutil.parser.parse(start_date).replace(tzinfo=datetime.timezone(offset=datetime.timedelta(hours=-4)))
        # now iso_start_date.isoformat() will give you exactly what you want
        iso_start_date =  dateutil.parser.parse(start_date).isoformat() + ISO_TIMEZONE
        iso_end_date =   dateutil.parser.parse(end_date).isoformat() + ISO_TIMEZONE
        
        # I don't like to mix string concatenation and String.format
        # This would look better as
        # endpoint = "{base_url}/{orders_endpoint}".format(base_url=self.base_url, orders_endpoint=ORDERS_ENDPOINT)
        # As for the params, you're using requests, so you can just pass them in as a dict in the requests.get call
        # requests.get(endpoint, headers=self.headers, params={'startDate' : iso_start_date, 'endDate' : iso_end_date})
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
        
        # this would be easier to read using String.format
        # that goes for most strings that are concantenations of more than a few strings
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

