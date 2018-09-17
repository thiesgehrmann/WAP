import json
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

import Events as Events

###########################
# Create a class to handle the y-axis for events on the same day

class AppState(object):

    class DayIndex(object):
        """
        Get counts per individual days
        """

        def __init__(self):
            self.days = {}
            self.idx  = {}
        #edef

        def __call__(self, event):
            if event.ID in self.idx:
                return self.idx[event.ID]
            #fi

            k = (event.day, event.month)
            if k not in self.days:
                self.days[k] = 0
            #fi

            self.days[k] = self.days[k] + 1
            self.idx[event.ID] = self.days[k]
            return self.days[k]
        #edef

        def max(self):
            m = max(self.days.values())
            print("MAX %d" % m)
            return m
        #edef
    #eclass

    def __init__(self):
        self.di = self.DayIndex()
        self.lastClickEvent = datetime.datetime.now() - datetime.timedelta(seconds=10)
        self.buttonCounts = {}
        self.refreshEvents()
    #edef

    def getButtonCount(self, id):
        if id not in self.buttonCounts:
            self.buttonCounts[id] = 0
        #fi
        return self.buttonCounts[id]
    #edef

    def incrementButtonCount(self, id):
        self.buttonCounts[id] = self.getButtonCount(id) + 1
    #edef
            
    def refreshEvents(self):
        events = Events.EventStructure([ e.standard() for Source in Events.sources for e in Source(redo=True) ]) 
        self.events = events.query(startDate=datetime.datetime.today())
#eclass

###########################
# Load WAP events and remove those before today

app = dash.Dash()

aState = AppState()

###########################
# Create the query panel

queryPanel = html.Div(children=[
    dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=aState.events.firstDate,
        max_date_allowed=aState.events.lastDate,
        start_date=aState.events.firstDate,
        end_date=aState.events.lastDate
    ),
    dcc.Dropdown(
        id='source-picker',
        options = [ {'label': source, 'value' : source } for source in sorted(aState.events.sources) ],
        multi=True,
        value=sorted(aState.events.sources)),
    dcc.Dropdown(
        id='category-picker',
        options=[ { 'label' : cat, 'value' : cat } for cat in sorted(aState.events.categories) ],
        multi=True,
        value=sorted(aState.events.categories)
    ),
    dcc.Dropdown(
        id='city-picker',
        options=[ { 'label' : city, 'value' : city } for city in sorted(aState.events.cities) ],
        multi=True,
        value=sorted(aState.events.cities)
    ),
    dcc.Checklist(
        id='bookable-picker',
        options=[
            {'label': 'Only Bookable', 'value': True}
        ],
        values=[]
    ),
    html.Button('Refresh', id='refresh-button'),
    html.Button('Reset', id='reset-button')
    ],
    style={'width': '20%', 'display': 'inline-block', 'vertical-align': 'middle'})

###########################
# Create the WAP scatter plot

def getFigureData(events):
    return {
            'data': [
                go.Scatter(
                    x=[ e.date for e in events if cat in e.categories ],
                    y=[ aState.di(e) for e in events if cat in e.categories ],
                    text=[ '%s, %s, %s' % (e.title, e.location, e.city) for e in events if cat in e.categories ],
                    customdata=[ e.ID for e in events if cat in e.categories ],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=cat
                ) for cat in sorted(aState.events.categories) # (Here use full-scope wap object because we want to maintain the category colors)
            ],
            'layout': {
                'margin': {'l': 15, 'r': 0, 'b': 15, 't': 5},
                'dragmode': 'select',
                'hovermode': 'closest',
                'yaxis' : {'range' : [0, aState.di.max() + 1]},
                'xaxis' : {'range' : [aState.events.firstDate-datetime.timedelta(days=1), aState.events.lastDate+datetime.timedelta(days=1)]},
                'displayModeBar': False
            }
        }
#edef

graphPanel = dcc.Graph(
                id='calendar',
                figure=getFigureData(aState.events),
                style={'width': '79%', 'display': 'inline-block', 'vertical-align': 'middle'}
            )

###########################
# Create the event information panel

def drawEvent(event):
    return [html.Div(children=[html.Img(src=event.image, style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top', 'height' : '100%'}),
                               html.Div(children=[html.Div([html.H2(event.title)]),
                                                  html.Div(str(event.date)),
                                                  html.Div(['%s, %s' % (event.location, event.city)]),
                                                  html.A(href=event.url, children=["We Are Public event"])],
                                        style={'width': '54%', 'display': 'inline-block', 'vertical-align': 'top'})
                               ]
                    )
            ]
#edef

def openEvent(event):
    return [html.Iframe(src=event.url, height='100vh', style={'width': '100%', 'vertical-align': 'top', 'height' : '100vh'})]
#edef


eventPanel = html.Div(id='eventPanel', children=[])

###########################
###########################
#Create the layout

app.layout = html.Div(children=[html.Div(children=[html.H1('We Are Public Dashboard')], style={'height' : '5vh', 'display': 'flex'}),
                                html.Div(children=[graphPanel, queryPanel], style={'height' : '40vh', 'display': 'flex'}),
                                html.Div(children=[eventPanel], style={'height' : '54vh'})
                            ],
                      style={'height' : '100vh'})

###########################
# Callbacks

@app.callback( Output('eventPanel', 'children'), [Input('calendar', 'hoverData'), Input('calendar', 'clickData')])
def display_event_data_callback(hoverData, clickData):

    print("HoverData: ", hoverData)
    print("ClickData: ", clickData)
    #print("PersistentEventID: ", persistentEventID)

    clickEventID = None if clickData is None else clickData['points'][0]['customdata']
    hoverEventID = None if hoverData is None else hoverData['points'][0]['customdata']

    currentEvent = datetime.datetime.now()

    if (currentEvent - aState.lastClickEvent) < datetime.timedelta(seconds=10):
        hoverEventID = None
    else:
        aState.lastClickEvent == None
    #fi


    if (clickEventID is None) and (hoverEventID is None):
        return [html.Div()]
    elif clickEventID == hoverEventID:
        aState.lastClickEvent = currentEvent
        return openEvent(aState.events[clickEventID])
    else:
        return drawEvent(aState.events[hoverEventID])
    #fi
#edef


@app.callback( Output('calendar', 'figure'),
                [ Input('source-picker', 'value'),
                  Input('date-picker-range', 'start_date'),
                  Input('date-picker-range', 'end_date'),
                  Input('category-picker', 'value'),
                  Input('city-picker', 'value'),
                  Input('bookable-picker', 'values'),
                  Input('reset-button', 'n_clicks'),
                  Input('refresh-button', 'n_clicks') ] )
def query(sources, start_date, end_date, categories, cities, bookable, reset_clicks, refresh_clicks):

    if (refresh_clicks is not None) and (refresh_clicks > aState.getButtonCount('refresh-button')):
        aState.refreshEvents()
        aState.incrementButtonCount('refresh-button')
    #fi

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    bookable = True if (True in bookable) else None

    return getFigureData(aState.events.query(startDate=start_date,
                                             endDate=end_date,
                                             bookable=bookable,
                                             city=cities,
                                             category=categories,
                                             sources=sources))
 #edef

###########################
# Start the server

app.run_server()
