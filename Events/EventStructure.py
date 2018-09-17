from .BIU import biu

class EventStructure(object):

    def __init__(self, events):
        self.events = events
        self.eventsIDX = { e.ID : e for e in events }
    #edef
    
    def __getitem__(self, ID):
        return self.eventsIDX[ID]
    #edef
    
    def __iter__(self):
        return self.events.__iter__()
    #edef
    
    def query(self, city=None,
              sources=None,
              startDate=None,
              endDate=None,
              category=None,
              bookable=None):
        """Retrieve only events which match certain criteria
        Inputs: city: String or lists of strings of city names
                startDate : datetime object for starting date
                endDate : Datetime object for ending date
                category: String or lists of strings of categories,
                bookable: Only the bookable events"""
        city     = [ city ] if isinstance(city, str) else city
        category = [ category ] if isinstance(category, str) else category
        
        relEvents = [ e for e in self.events if
                        ( (city is None)      or (e.city in city)         ) and
                        ( (sources is None)   or (e.source in sources)    ) and
                        ( (startDate is None) or (e.date >= startDate)   ) and
                        ( (endDate is None)   or (e.date <= endDate)     ) and
                        ( (category is None)  or len(set(e.categories) & set(category)) > 0 ) and
                        ( (bookable is None)  or (e.bookable == bookable) ) ]
        
        return EventStructure(relEvents)
    #edef
    
    @property
    def sources(self):
        return [ c for c in biu.processing.lst.uniq([ e.source for e in self.events ]) if c is not None ]
            
    
    @property
    def categories(self):
        return [ c for c in 
                  biu.processing.lst.uniq(biu.processing.lst.flatten([ e.categories for e in self.events ]))
                 if c is not None ]
    #edef

    @property
    def cities(self):
        return [ c for c in biu.processing.lst.uniq([ e.city for e in self.events ]) if c is not None ]
    #edef
    
    
    @property
    def months(self):
        return biu.processing.lst.uniq([ e.month for e in self.events])
    #edef
    
    @property
    def firstDate(self):
        return min(self.events, key=lambda e: e.date).date
    #edef

    @property
    def lastDate(self):
        return max(self.events, key=lambda e: e.date).date
    #edef  