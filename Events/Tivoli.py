from .BIU import biu
import pandas as pd

import json
from collections import namedtuple
import datetime

from . import StandardEvent as StandardEvent

class Tivoli(object):
    class Event(object):
        def __init__(self, data):
            self.data = data
        #edef
        
        def standard(self):
            #ID, source, title, city, location, date, time, categories, url, bookable, image):
            day   = int(self.data['day'].split(' ')[-1])
            year  = int(self.data['year'])
            month = int(self.data['yearMonth'][4:])
            return StandardEvent.StandardEvent(self.data['name'] + 'Tivoli', 'Tivoli',self.data['title'], 'Utrecht',
                                               'Tivoli', datetime.datetime(year, month, day), '0:0:0', ['Tivoli'],
                                               self.data['link'],
                                               False, self.data['image'])
             
        #edef
    #eclass
        
    
    def __init__(self, events=None, redo=False):
        if events is None:
            events = self.__retrieveEvents(redo)
        #fi0
        self.events = events
        
        self.__idx = None#{ e.id : i for (i,e) in enumerate(self.events) }
    #edef
    
    def __getitem__(self, ID):
        return self.eventsIDX[ID]
    #edef
    
    def __iter__(self):
        return self.events.__iter__()
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
