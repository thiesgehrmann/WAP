from .BIU import biu
import pandas as pd

import json
from collections import namedtuple
import datetime

class Tivoli(object):
    class Event(object):
        def __init__(self, data):
            
            self.data = data
           #edef
    
    def __init__(self, events=None, redo=False):
        if events is None:
            events = self.__retrieveEvents(redo)
        #fi0
        self.events = events
        
        self.__idx = None#{ e.id : i for (i,e) in enumerate(self.events) }
    #edef
    
    def __retrieveEvents(self, redo):
        eventList = []
        for page in range(1,15):
            ao = biu.utils.Acquire(redo=redo).curl('https://www.tivolivredenburg.nl/wp-admin/admin-ajax.php?action=get_events&page=%d&categorie=' % page)
            eventList.extend(json.load(open(ao.acquire(),'r')))
        #efor
        #eventList = biu.processing.lst.uniq(eventList, key=lambda x: x['permalink'])
        return [ self.Event(data) for data in eventList]
    #edef
