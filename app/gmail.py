import httplib2
from apiclient import discovery
from apiclient.errors import HttpError
import base64

class GMail(object):

    def __init__(self,credentials,user_id):
        credentials = credentials
        http = httplib2.Http()
        http = credentials.authorize(http)
        self.service = discovery.build('gmail', 'v1', http=http)
        self.user_id = user_id    

    def getLabels(self):
        response = self.service.users().labels().list(userId=self.user_id).execute()
        return response['labels']

    def getMessageIdsByLabel(self,labelIds):
        response = self.service.users().messages().list(userId=self.user_id,labelIds=labelIds,maxResults=10).execute()
        if 'messages' in response:
            return response['messages']
        else:
            return []

    def getMessage(self,messageId):
        message = self.service.users().messages().get(userId=self.user_id, id=messageId, format='full').execute()
        return message
    

    @staticmethod
    def getMessageTextFromMessage(message):
        part =  message['payload']['parts'][0]
        
        if 'parts' in part:
            part = part['parts'][0]
        
        return base64.urlsafe_b64decode(part['body']['data'].encode("ASCII"))
        
        

    @staticmethod
    def getMessageSubjectFromMessage(message):
        headers = message['payload']['headers']

        for header in headers:
            if header['name'] == 'Subject':
                return header['value']
    