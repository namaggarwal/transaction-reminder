from requests import Request, Session
from requests_oauthlib import OAuth2Session
from model import List, Task
import json


class WunderList(object):

    AUTH_URL = 'https://www.wunderlist.com/oauth/authorize'
    TOKEN_URL = 'https://www.wunderlist.com/oauth/access_token'
    BASE_URL = 'http://a.wunderlist.com/api/v1'
    LISTS_URL = BASE_URL+'/lists'
    REMINDERS_URL = BASE_URL + '/reminders'
    TASK_URL = BASE_URL + '/tasks'

    def __init__(self,client_id, access_token=None):
        
        self.client_id = client_id
        self.access_token = access_token
        self.session = Session()

        headers = {
            'X-Access-Token': access_token,
            'X-Client-ID': client_id
        }
        self.service = Request('POST',headers = headers)


    def get_authorize_url(self,redirect_uri):
        return OAuth2Session(self.client_id,redirect_uri=redirect_uri).authorization_url(WunderList.AUTH_URL)

    def fetch_token(self,secret,state,response_url):
        oauth = OAuth2Session(self.client_id,state=state)
        token = oauth.fetch_token(WunderList.TOKEN_URL, client_secret=secret,
                                    authorization_response=response_url)

        return token['access_token']

    def get_lists(self):
        url = WunderList.LISTS_URL
        self.service.url = url
        self.service.method = 'GET'
        prepReq = self.service.prepare()
        response =  self.session.send(prepReq)
        response = json.loads(response.content)
        lists = []

        for wl in response:
            lists.append(List(wl))

        return lists

    
    def get_reminders_by_list(self,list_id):

        url = WunderList.REMINDERS_URL+'?list_id='+str(list_id)
        self.service.url = url
        self.service.method = 'GET'
        prepReq = self.service.prepare()
        response =  self.session.send(prepReq)
        response = json.loads(response.content)
        return response

    def get_tasks_by_list(self,list_id):

        url = WunderList.TASK_URL+'?list_id='+str(list_id)
        self.service.url = url
        self.service.method = 'GET'
        prepReq = self.service.prepare()
        response =  self.session.send(prepReq)
        response = json.loads(response.content)

        tasks = []

        for wl in response:
            tasks.append(Task(wl))

        return tasks

    
    def create_list(self,wlist):
        self.service.url = WunderList.LISTS_URL
        self.service.json = wlist.get_json()
        self.service.method = 'POST'
        prepReq = self.service.prepare()
        response =  self.session.send(prepReq)
        response = json.loads(response.content)
        print response
        return List(response)


    def create_task(self,task):
        self.service.url = WunderList.TASK_URL
        self.service.json = task.get_json()
        self.service.method = 'POST'
        prepReq = self.service.prepare()
        response =  self.session.send(prepReq)
        return response




       




    