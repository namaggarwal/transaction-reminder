from model import User, Label
from oauth2client import client
from gmail import GMail
import datetime
import utils
import logging
import httplib2
import calendar
import re
from wunderlist import WunderList, Task, List
from logger import Logger

class TransactionScheduler(object):

    @staticmethod
    def getGoogleCredentials(app, user):

        tokenExpiry = utils.stringToDatetime(user.googleTokenExpiry)

        googlecredentials = client.GoogleCredentials(
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
            access_token=user.googleAccessToken,
            refresh_token=user.googleRefreshToken,
            token_expiry=tokenExpiry,
            token_uri=user.googleTokenURI,
            revoke_uri=user.googleRevokeURI,
            user_agent=None
        )

        if googlecredentials.access_token_expired:
            app.logger.debug("Google credentials for %s expired. Asking for new token",user.email)
            http = httplib2.Http()
            googlecredentials.refresh(http)
            user.googleAccessToken = googlecredentials.access_token
            user.googleTokenExpiry = utils.datetimeToString(googlecredentials.token_expiry)
            user.save()

        return googlecredentials

    def execute(self,app):
        with app.app_context():
            users = User.query.filter_by(googleEmailAccess=True,wunderListAccess=True).all()

            for user in users:

                app.logger.debug("Scanning transactions for %s",user.email)
                
                #Get google credentials of user
                try:
                    googlecredentials = TransactionScheduler.getGoogleCredentials(app,user)
                except Exception as e:
                    app.logger.error("Error getting Google credentials of user "+user.email)
                    user.googleEmailAccess = False
                    user.save()
                    continue
                
                #Create Gmail object
                gmail = GMail(googlecredentials,user.email)
                
                supportedLabels = set(["Bank/SC"])
                
                userLabels =  Label.query.filter_by(user_id=user.id).all()        
                userLabelsName = set(map(lambda u: u.name, userLabels))

                notAddedLabels = supportedLabels - userLabelsName

                if len(notAddedLabels) > 0:

                    #Fetch labels from remote
                    remoteLabels = gmail.getLabels()

                    for label in remoteLabels:

                        if label['name'] in notAddedLabels:

                            newLabel = Label()
                            newLabel.name = label['name']
                            newLabel.label_id = label['id']
                            user.labels.append(newLabel)
                            user.save()
                    
                    userLabels =  Label.query.filter_by(user_id=user.id).all() 
                
                
                for label in userLabels:

                    messageIds = gmail.getMessageIdsByLabel([label.label_id])
                    lastReadMessage = label.last_message_read if label.last_message_read else -1
                    for messageId in messageIds:
                        if messageId["id"] == lastReadMessage:
                            break
                        #Set last read message to top of the list
                        label.last_message_read = messageIds[0]["id"]

                        message = gmail.getMessage(messageId["id"])
                        
                        if label.name == "Bank/SC":

                            curr, amount, place = self.handleSCMessages(message)

                            if curr is not None:

                                self.createReminder(app,user,curr+" "+amount,place)
                    
                    label.save()

                app.logger.debug("Scanning transactions completed for %s",user.email)

                

    def handleSCMessages(self,message):

        subject = GMail.getMessageSubjectFromMessage(message)
        if subject == "Transaction Alert Primary / Supplementary Card Email Alert":

            text = GMail.getMessageTextFromMessage(message)
            pattern = re.compile(r".*charging \+(.*) (\d+\.\d+) .* at (.*)\..*")
            result = pattern.findall(text)
            amount = None
            if len(result) > 0:
                return result[0]

        
        return (None,None,None)

    def createReminder(self,app,user,amount,place):

        app.logger.debug("Creating reminder")

        wl = WunderList(app.config["WUNDERLIST_CLIENT_ID"],user.wunderListToken)

        if not user.wunderListId or user.wunderListId == "":
            lists = wl.get_lists()

            for wlist in lists:
                if wlist.get_title() == app.config["WUNDERLIST_NAME"]:
                    user.wunderListId = wlist.get_id()
                    user.save()
                    break
    
        #If list is still not there 
        #we need to create a list
        if not user.wunderListId:

            wlist = List()
            wlist.set_title(app.config["WUNDERLIST_NAME"])
            wlist = wl.create_list(wlist)
            user.wunderListId = wlist.get_id()
            user.save()

        rem = amount + " at "+place
        task = Task()
        task.set_list_id(user.wunderListId)
        task.set_title(rem)
        task.set_due_date(datetime.datetime.today())
        wl.create_task(task)