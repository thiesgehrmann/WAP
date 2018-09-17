import datetime

class StandardEvent(object):
    
    def __init__(self, ID, source, title, city, location, date, time, categories, url, bookable, image):
        self.ID         = ID
        self.source     = source
        self.title      = title
        self.city       = city
        self.location   = location
        self.date       = date
        self.time       = time
        self.categories = categories
        self.url        = url
        self.bookable   = bookable
        self.image      = image
        self.day        = self.date.strftime('%d')
        self.month      = self.date.strftime('%m')
    #edef
    
#eclass
