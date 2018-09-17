from BIU import biu
import pandas as pd

import json
from collections import namedtuple
import datetime

class WeArePublic(object):
    
    class Event(object):

        def __init__(self, data):
            self.data = data
            self.extracted = {}
        #edef

        eventTupleType = namedtuple('WAPEvent', ['ID', 'title', 'day', 'month', 'date', 'price', 'bookable', 'url', 'category', 'location', 'city'])

        @property
        def tuple(self):
            return self.eventTupleType(self.id, self.title, self.day, self.month, self.dtime, self.price, self.bookable, self.url, self.category, self.location, self.city)
        
        
        #def __getattr__(self, key):
        #    if key in self.data:
        #        return self.data[key]
        #    #fi
        #    print("COULD NOT FIND %s" % key)
        #    raise ValueError
        #edef

        @property
        def id(self):
            return self.data['id']
        

        @property
        def title(self):
            return self.data['title']
        #edef
        
        
        @property
        def url(self):
            return self.data['permalink']
        #edef

        @property
        def permdata(self):
            if 'permdata' not in self.extracted:
                d = open(biu.utils.Acquire().curl(self.url).acquire(), 'r').read()
                self.extracted['permdata'] = d
            #fi
            return self.extracted['permdata']
        #edef
        
        @property
        def date(self):
            if 'date' not in self.extracted:
                self.extracted['date'] = self.data['date']['day'].split('>')[-1]
            #fi
            return self.extracted['date']
        
        @property
        def day(self):
            if 'day' not in self.extracted:
                self.extracted['day'] = int(self.date.split(' ')[0])
            #fi
            return self.extracted['day']
        #edef
        
        @property
        def month(self):
            if 'month' not in self.extracted:
                self.extracted['month'] = self.date.split(' ')[1]
            #fi
            return self.extracted['month']
        #edef

        @property
        def year(self):
            return datetime.today().year
        #edef

        __monthMap = dict( [ (m,i+1) for (i,m) in enumerate(['jan', 'feb', 'mar', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']) ] )
        @property
        def dtime(self):
            return datetime.datetime(2018, self.__monthMap[self.month], self.day)
        #edef
        
        @property
        def category(self):
            cat = [ c.strip() for c in self.data['lang_term_names'] if c is not None ] if ('lang_term_names' in self.data) else []
            return cat
        #edef
        
        @property
        def location(self):
            if 'location' not in self.extracted:
                loc = self.data['location']['location'].strip() if isinstance(self.data['location']['location'], str) else 'Unknown'
                loc = loc.strip()
                if loc is '':
                    loc = 'Diverse'
                #fi
                self.extracted['location'] = loc
            #fi
            return self.extracted['location']
        #edef
        #edef
        
        @property
        def city(self):
            if 'city' not in self.extracted:
                city = self.data['location']['city'].strip() if isinstance(self.data['location']['city'], str) else 'Unknown'
                city = city.strip()
                if city is '':
                    city = 'Diverse'
                #fi
                self.extracted['city'] = city
            #fi
            return self.extracted['city']
        #edef
        
        @property
        def price(self):
            if 'price' not in self.extracted:
                lines = [line for line in self.permdata.split('\n') if 'meta' not in line]
                relLine = [ line for line in lines if ('voor We Are Public-leden' in line) ]
                if len(relLine) == 0:
                    relLine = [ line for line in lines if ('toegang' in line) ]
                #fi
                
                if len(relLine) == 0:
                    relLine = [ 'vrij' ]
                #fi
                relLine = relLine[0].lower()
                price = 0
                if 'vrij' not in relLine:
                    price = relLine.split()[0].split('>')[-1].strip()
                    if price in ['vrij', 'vrije', 'exclusief']:
                        price = 0
                    else:
                        price = float(price[1:].replace(',', '.'))
                    #fi
                #fi
                self.extracted['price'] = price
            #fi
            return self.extracted['price']
        #edef                
        
        @property
        def bookable(self):
            if 'bookable' not in self.extracted:
                b = 'Kaartje reserveren' in self.permdata
                self.extracted['bookable'] = b
            #fi
            return self.extracted['bookable']
        #edef

        @property
        def thumbnail(self):
            return self.data['thumbnail']['event'].split('"')[1]
        #edefªº
        
        
        def __getitem__(self, key):
            return self.data[key]
        #edef
        
        #def _repr_pretty_(self, *pargs):
        #    return self.data['thumbnail']['event']
        #edef
        
        def _repr_html_(self):
            print("NOW IN REPR HTML")
            return '<div>' + self.data['thumbnail']['event'] + '</div>'
        #edef
        
        def __repr__(self):
            return str(self)
        #edef
        
        def __str__(self):
            dstr  = "WAP Event\n"
            dstr += " Title:    %s\n" % self.title
            dstr += " Date:     %s\n" % self.date
            dstr += " Location: %s\n" % self.location
            dstr += " City:     %s\n" % self.city
            dstr += " Bookable: %s\n" % ('Yes' if self.bookable else 'No')
            dstr += " URL:      %s\n" % self.url
            dstr += " Category: %s\n" % ' | '.join(self.category)
            return dstr
        #edef
        
    #eclass
    
    def __init__(self, events=None, redo=False):
        if events is None:
            events = self.__retrieveEvents(redo)
        #fi0
        self.events = events
        
        self.__idx = { e.id : i for (i,e) in enumerate(self.events) }
    #edef
    
    def __retrieveEvents(self, redo):
        eventList = []
        for page in range(1,15):
            ao = biu.utils.Acquire(redo=redo).curl('https://www.wearepublic.nl/wp-json/wearepublic/v1/events/?page=%d&search=' % page)
            eventList.extend(json.load(open(ao.acquire(),'r')))
        #efor
        eventList = biu.processing.lst.uniq(eventList, key=lambda x: x['permalink'])
        return [ self.Event(data) for data in eventList]
    #edef
    
    def bookables(self):
        return WeArePublic(events=[ e for e in self.events if e.bookable ])
    #edef
    
    def query(self, city=None,
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
                        ( (startDate is None) or (e.dtime >= startDate)   ) and
                        ( (endDate is None)   or (e.dtime <= endDate)     ) and
                        ( (category is None)  or len(set(e.category) & set(category)) > 0 ) and
                        ( (bookable is None)  or (e.bookable == bookable) ) ]
        
        return WeArePublic(relEvents )
    #edef
    
    @property
    def categories(self):
        return [ c for c in 
                  biu.processing.lst.uniq(biu.processing.lst.flatten([ e.category for e in self.events ]))
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
    def calendar(self):
        import pandas as pd
        cal = { m : [ "" for i in range(31) ] for m in self.months }
        for e in self.events:
            cal[e.month][e.day-1] = cal[e.month][e.day-1] + ' ' + str(e.id)
        #efor
        df = pd.DataFrame.from_dict(cal)
        df.index = df.index+1
        return df
    #edef
    
    @property
    def table(self):
        data = [ [ str(f) for f in e.tuple ] for e in self.events ]
        return pd.DataFrame(data, columns=self.Event.eventTupleType).set_index('ID')
    #edef

    @property
    def firstDate(self):
        return min(self.events, key=lambda e: e.dtime).dtime
    #edef

    @property
    def lastDate(self):
        return max(self.events, key=lambda e: e.dtime).dtime
    #edef   

    def __iter__(self):
        return self.events.__iter__()
    #edef    
    
    def __getitem__(self, key):
        return self.events[self.__idx[key]]
    #edef
    
    def _repr_html_(self):
        return self.table._repr_html_()
    #edef
    
    def __repr__(self):
        return str(self)
    #edef
    
    def __str__(self):
        dstr = "WeArePublic Events\n"
        dstr += '\n'.join([ ' (%5d)%s <%s> %s' % (e.id, '[B]' if e.bookable else '   ', e.date, e.title) for (i,e) in enumerate(self.events) ])
        return dstr
    #edef
    
#eclass