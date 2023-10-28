import requests, json, os
from bs4 import BeautifulSoup
from .nebutil.time import DateUtil
from .nebutil.log import LOGGER
from .nebutil import serializer
from .events import DataEvent as Event, DataEventCollection as EventCollection, URL

DATA_FILE = "events.json"

def getData(downloadImgs=True):
    response = requests.get(URL).text
    LOGGER.info(f"Succesfully downloaded {URL} content.")
    soup = BeautifulSoup(response, 'html5lib')
    
    eventsDiv = {
        'current': soup.select_one("body div.page-content div.current-events"),
        'upcoming': soup.select_one("body div.page-content div.upcoming-events")
    }
    
    if eventsDiv['current'] is None or eventsDiv['upcoming'] is None:
        LOGGER.error("Error while parsing HTML. Exiting...")
        exit(1)
        
    EVENT_WRAPPER_CLASS = 'span.event-header-item-wrapper'
    currentEventsLength = len(eventsDiv['current'].select(EVENT_WRAPPER_CLASS))
    upcomingEventsLength = len(eventsDiv['upcoming'].select(EVENT_WRAPPER_CLASS))
    LOGGER.info(f"Processing {currentEventsLength} current events and {upcomingEventsLength} upcoming events...")
    
    events = []
    for k,v in eventsDiv.items():
        if v is not None:
            eventSet = v.select('span.event-header-item-wrapper')
            for index,event in enumerate(eventSet):
                event = Event.fromSoup(k,event)
                if event:
                    events.append(event)
    
    LOGGER.info(f"Successfully processed {len(events)} events.")
    events = EventCollection(events)
    if downloadImgs:
        path = os.path.join(os.getcwd(),'assets')
        events.downloadImgs(path)
    nextUpdate:float = min([ev.startDateTimestamp for ev in events.upcoming() if ev.startDateTimestamp])
    return events, nextUpdate
    
def removePastEvents(events:EventCollection):
    toRemove = events.filter(lambda ev: ev.endDateTimestamp < DateUtil.now().timestamp)
    LOGGER.info(f"Found {toRemove.size} past events.")
    if toRemove.size > 0:
        LOGGER.info("Removing past events...")
        events -= toRemove
        LOGGER.info(f"Removed past events. {events.size} events remaining.")
    return events

def save(events,nextUpdate):
    try:
        with open(DATA_FILE,'w') as f:
            events = removePastEvents(events)
            LOGGER.info(f"Next update: {DateUtil.fromTimestamp(nextUpdate)}")
            events = events.sort(lambda ev: ev.startDateTimestamp,False)
            json.dump({
                'nextUpdate': nextUpdate,
                'events': events
            },f,indent=4,default=serializer)
            LOGGER.info(f"Saved {events.size} events.")
        return 1
    except Exception as e:
        LOGGER.error(f"Error while saving data: {e} - {e.__traceback__}")
        return 0
    
def read():
    events = None
    nextUpdate = 0.
    with open(DATA_FILE,'r') as f:
        data = json.loads(f.read())
        eventsData = data['events']['items']
        nextUpdate:float = data['nextUpdate']
        events = EventCollection([Event(**event) for event in eventsData])
    return events, nextUpdate

def load(downloadImages=True):
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        events, nextUpdate = read()
        LOGGER.info('Data file found. Reading...')
        now = DateUtil.now().timestamp
        if nextUpdate < now:
            LOGGER.info("File data is outdated. Updating...")
            events,nextUpdate = getData(downloadImages)
            save(events,nextUpdate)
            events = read()[0]
        else:
            LOGGER.info("File data is up to date.")
            LOGGER.info(f"Next update: {DateUtil.fromTimestamp(nextUpdate)}")
        events = removePastEvents(events)
    else:
        LOGGER.info('Data file not found. Downloading...')
        events,nextUpdate = getData(downloadImages)
        save(events,nextUpdate)
    LOGGER.info(f"Found {events.size} events.")
    return events
