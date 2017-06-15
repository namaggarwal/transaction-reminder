
class WL(object):

    def __init__(self,data=None):

        if data:
            self.id = data['id']
            self.title = data['title']
            self.created_at = data['created_at']

        
    def get_id(self):
        return self.id

    def get_title(self):
        return self.title
    
    def get_created_at(self):
        return self.created_at

    def set_title(self,title):
        self.title = title



class List(WL):

    def __init__(self,data=None):
        super(List, self).__init__(data)

    def get_json(self):

        wlist = {
            'title': self.title
        }
        
        return wlist
    
class Task(WL):

    def __init__(self,data=None):

        super(Task, self).__init__(data)

        if data:

            self.list_id = data['list_id']
        
    def get_list_id(self):
        return self.list_id

    def set_list_id(self,list_id):
        self.list_id = list_id
    
    def set_due_date(self,due_date):
        self.due_date = due_date

    def get_json(self):
        task =  {
            'list_id': int(self.list_id),
            'title': self.title
        }

        if(self.due_date):
            task['due_date'] = str(self.due_date.year)+"-"+str(self.due_date.month)+"-"+str(self.due_date.day)

        return task
        


