import requests
from ..nebutil import Serializable
from ..nebutil.time import DateUtil
from ..nebutil.log import LOGGER
from ..nebutil.collections import Collec
from typing import Callable, Dict,Any
from bs4 import BeautifulSoup, Tag
from typing import Any, Dict, Iterator, Sequence, Union, Optional, List

URL = "https://leekduck.com/events/"


class EventType(Serializable):
    SPOTLIGHT_HOUR = 'SPOTLIGHT_HOUR'
    RAID_HOUR = 'RAID_HOUR'
    RAID_BATTLES = 'RAID_BATTLES'
    COMMUNITY_DAY = 'COMMUNITY_DAY'
    SEASON = 'SEASON'
    
    @staticmethod
    def all() -> list[str]:
        return list(EventType.__dict__.values())
    
    @staticmethod
    def raids():
        """
        Returns a list of all raid event types.

        :return: A list of all raid event types.
        :rtype: `list[str]`
        """
        return [EventType.RAID_HOUR,EventType.RAID_BATTLES]

class DataEvent(Serializable):
    """
    Represents a Pokemon Go event.
    
    :param name: The name of the event.
    :type name: `str`
    :param startDate: The start date of the event.
    :type startDate: `str`
    :param endDate: The end date of the event.
    :type endDate: `str`
    :param localtime: Whether the event is in local time or not.
    :type localtime: `bool`
    :param eventType: The type of the event.
    :type eventType: `str`
    :param content: The content of the event.
    :type content: `Dict[str,Any]`
    :param url: The URL of the event.
    :type url: `str`
    :param imgUrl: The URL of the image of the event.
    :type imgUrl: `str`
    """
    
    ALTERNATE_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    def __init__(self,name:str,startDate:str,endDate:str,localtime:bool,eventType:str,content:Dict[str,Any],url:str,imgUrl:str):
        self.__name = name
        try:
            self.__startDate = DateUtil.fromStr(startDate).toStr
        except ValueError:
            self.__startDate = DateUtil.fromStr(startDate,DataEvent.ALTERNATE_DATE_FORMAT).toStr
        try:
            self.__endDate = DateUtil.fromStr(endDate).toStr
        except ValueError:
            self.__endDate = DateUtil.fromStr(endDate,DataEvent.ALTERNATE_DATE_FORMAT).toStr
        self.__localtime = localtime
        self.__eventType = eventType
        self.__content = content
        self.__url = url
        self.__imgUrl = imgUrl
    
    @property
    def name(self):
        return self.__name
    
    @property
    def startDate(self):
        return self.__startDate
    
    @property
    def startDateTimestamp(self):
        return DateUtil.fromStr(self.startDate,DataEvent.ALTERNATE_DATE_FORMAT).timestamp
    
    @property
    def endDate(self):
        return self.__endDate
    
    @property
    def endDateTimestamp(self):
        return DateUtil.fromStr(self.endDate,DataEvent.ALTERNATE_DATE_FORMAT).timestamp
    
    @property
    def localtime(self):
        return self.__localtime
    
    @property
    def eventType(self):
        return self.__eventType
    
    @property
    def content(self):
        return self.__content
    
    @property
    def url(self):
        return self.__url
    
    @property
    def imgUrl(self):
        return self.__imgUrl
    
    def contentStr(self):
        s = ""
        for key,value in self.content.items():
            if key == 'featuredPokemons':
                continue
            
            if key == 'shinyEnabled':
                s += f"Shiny: {value}\n"
                continue
            else:
                s += f"{key.capitalize()}: "
            if key == 'bonuses' and len(value) == 0:
                s += "?\n"
                continue
            if isinstance(value,list):
                s += f"{', '.join(value)}\n"
            else:
                s += f"{value}\n"
        return s
    
    def downloadImg(self,path:str):
        response = requests.get(self.imgUrl)
        targetFile = f"{path}/{self.imgUrl.split('/')[-1]}"
        if response.status_code == 200:
            try:
                with open(targetFile, 'xb') as f:
                    f.write(response.content)
                LOGGER.info(f"Downloaded {targetFile}.")
            except FileExistsError:
                LOGGER.info(f"File {targetFile} already exists, skipping...")
    
    @classmethod
    def fromSoup(cls,timeDivKey,soup:Union[BeautifulSoup,Tag]):
        h5 = soup.select_one('h5') or Tag()
        a = soup.select_one('a')
        
        if h5 is None or a is None:
            LOGGER.error("Error while parsing HTML. Exiting...")
            return None
        
        if 'hide-event' not in a['class']:
            return None
        
        localtime = bool(h5.attrs['data-event-local-time'])
        
        href = URL + a.attrs['href'][len('/events/'):]
        name = a.find("h2").text
        
        eventType = a.select_one("div.event-item-wrapper").p.text.lower().replace("pokémon","").strip().replace(" ","_").upper()
        img = URL[:-len('/events')] + a.select_one("div.event-item-wrapper").img.attrs['src'][len('/cdn-cgi/image/fit=scale-down,height=95,quality=100,format=webp/'):]
        
        if timeDivKey == 'current':
            startDateStr = h5.attrs['data-event-start-date-check']
        else:
            startDateStr = h5.attrs['data-event-start-date']
            
        endDateStr = str(startDateStr)
        if h5.has_attr('data-event-end-date'):
            endDateStr = h5.attrs['data-event-end-date']
            # If event has already ended, skip it
            endDateTest = DateUtil.fromStr(endDateStr)
            if endDateTest.timestamp < DateUtil.now().timestamp:
                return None
        
        contentResponse = requests.get(href).text
        contentSoup = BeautifulSoup(contentResponse,'html5lib')
        content = DataEvent.processContent(eventType,contentSoup)
        
        ev = cls(name,startDateStr,endDateStr,localtime,eventType,content,href,img)
        with open('res.txt','a') as f:
            f.write(str(ev) + '\n')
        return ev
    
    @staticmethod
    def processContent(eventType:str,soup:Union[BeautifulSoup,Tag]):
        content:Dict[str,Any] = {}
        if eventType == EventType.RAID_BATTLES:
            features = soup.select("div.event-toc a:not(.event-toc-graphic)")
            targetIds = [e.attrs['href'][1:] for e in features]
            html = soup.select_one("#raids + * + ul.pkmn-list-flex")
            anyEltCount = 2
            while html is None:
                html = soup.select_one(f"#raids + {anyEltCount * '*+'} ul.pkmn-list-flex")
                anyEltCount += 1
            pkmnNames = html.select(".pkmn-name")
            pkmnNames = [e.text.replace(" and ","").replace(",","") for e in pkmnNames]
            # Put alternate forms at the end of each name
            pkmnNames = list(map(lambda e: e if ' ' not in e else e[e.index(' '):] + '_' + e[:e.index(' ')],pkmnNames))
            pkmnNames = [e.upper().replace(" ","") for e in pkmnNames if e]
            content['featuredPokemons'] = pkmnNames
            content['shinyEnabled'] = False
            if 'shiny' in targetIds:
                content['shinyEnabled'] = True
        elif eventType == EventType.RAID_HOUR:
            soup2 = soup.select_one("h1.page-title")
            processed = soup2.text
            processed = processed.split("Raid")[0].split(" and ")
            featuredPokemons = [s.strip().upper() for s in processed]
            content['featuredPokemons'] = featuredPokemons
        elif eventType == EventType.SPOTLIGHT_HOUR:
            soup2 = soup.select_one("div.event-description p:nth-child(2)")
            processed = soup2.text
            processed = processed.split(": ")[1]
            processed = processed.split(" and ")
            featuredPokemon, bonus = processed[0].split(" is ")[-1], processed[1].split(" is ")[-1][:-1]
            content['featuredPokemons'] = [featuredPokemon.upper()]
            content['bonuses'] = [bonus]
        elif eventType == EventType.COMMUNITY_DAY:
            content:Dict[str,Any] = {}
            processed = soup.select_one("article.event-page")
            featuredPokemon = processed.select_one("h1.page-title").text.split()[0].upper()
            bonuses = [e.text for e in processed.select("div.bonus-text")]
            bonuses = list(map(lambda e: e.replace("*","").strip(),bonuses))
            content['featuredPokemons'] = [featuredPokemon]
            content['bonuses'] = bonuses
        elif eventType == EventType.SEASON:
            pass
        return content   
    
    def __str__(self) -> str:
        return f'{self.name} ({self.startDate} - {self.endDate})'
    
    def __repr__(self) -> str:
        return f'Event({self.name},{self.startDate},{self.endDate},{self.localtime},{self.eventType},{self.content},{self.url},{self.imgUrl})'
    
    def __eq__(self,other) -> bool:
        if isinstance(other,DataEvent):
            return self.name == other.name and self.startDate == other.startDate and self.endDate == other.endDate and self.startDateTimestamp == other.startDateTimestamp and self.endDateTimestamp == other.endDateTimestamp
        return False
    
    def __hash__(self) -> int:
        return hash((self.name,self.startDate,self.endDate))
    
    def __bool__(self) -> bool:
        return bool(self.name and self.startDate and self.endDate)
    
    def __lt__(self,other) -> bool:
        if isinstance(other,DataEvent):
            return self.startDateTimestamp < other.startDateTimestamp
        return False
    
    def __le__(self,other) -> bool:
        if isinstance(other,DataEvent):
            return self.startDateTimestamp <= other.startDateTimestamp
        return False
    
    def __gt__(self,other) -> bool:
        if isinstance(other,DataEvent):
            return self.startDateTimestamp > other.startDateTimestamp
        return False
    
    def __ge__(self,other) -> bool:
        if isinstance(other,DataEvent):
            return self.startDateTimestamp >= other.startDateTimestamp
        return False
    
    def __ne__(self,other) -> bool:
        if isinstance(other,DataEvent):
            return self.name != other.name or self.startDate != other.startDate or self.endDate != other.endDate
        return False
    
    def __iter__(self):
        return iter((self.name,self.startDate,self.endDate,self.localtime,self.eventType,self.content,self.url,self.imgUrl))
    
    def __getitem__(self,key):
        return (self.name,self.startDate,self.endDate,self.localtime,self.eventType,self.content,self.url,self.imgUrl)[key]
    
    def __setitem__(self,key,value):
        raise NotImplementedError('Event is immutable')
    
    def __delitem__(self,key):
        raise NotImplementedError('Event is immutable')
    
    def __contains__(self,item):
        return item in (self.name,self.startDate,self.endDate,self.localtime,self.eventType,self.content,self.url,self.imgUrl)
    
    def __len__(self):
        return 8
    
class DataEventCollection(Collec, Serializable):
    def __init__(self, items: Iterator[DataEvent] | Sequence[DataEvent]) -> None:
        super().__init__(items)
    
    def filter(self, func: Callable[[DataEvent], bool]):
        return self.__class__(filter(func,self.items))
    
    def current(self,endingBefore:Optional[str],endingAfter:Optional[str],dateFormat="%Y-%m-%d"):
        """
        Returns a filtered collection of events that are currently active.
        
        :param endingBefore: Used to filter events that have an end date before the specified date. If this parameter is not provided, all events with end dates before the current date will be chosen.
        :type endingBefore: `Optional[str]`
        :param endingAfter:  Used to filter events that have an end date after the specified date. If this parameter is not provided, all events with end dates after the current date will be chosen.
        :type endingAfter: `Optional[str]`
        :param dateFormat: Used to specifythe format of the date of `endingBefore` and `endingAfter`. The default value is "%Y-%m-%d".
        :return: A filtered collection of events that are currently active.
        :rtype: `DataEventCollection`
        """
        if isinstance(endingBefore,str):
            endingBeforeTimeStamp = DateUtil.fromStr(endingBefore,dateFormat).timestamp
        if isinstance(endingAfter,str):
            endingAfterTimestamp = DateUtil.fromStr(endingAfter,dateFormat).timestamp
        now = DateUtil.now().timestamp
        return self.filter(lambda ev: (ev.startDateTimestamp <= now and ev.endDateTimestamp > now) and (endingBeforeTimeStamp is None or ev.endDateTimestamp <= endingBeforeTimeStamp) and (endingAfterTimestamp is None or ev.endDateTimestamp >= endingAfterTimestamp))


    def upcoming(self,before=None,after=None,dateFormat="%Y-%m-%d"):
        """
        Returns a filtered collection of the upcoming events.

        :param before: Used to filter events that have a start date before the specified date. If this parameter is not provided, all events with start dates before the current date will be chosen.
        :type before: `Optional[str]`
        :param after:  Used to filter events that have a start date after the specified date. If this parameter is not provided, all events with start dates after the current date will be chosen.
        :type after: `Optional[str]`
        :param dateFormat: The `dateFormat` parameter is a string that specifies the format of the date of `before` and `after`. The default value is "%Y-%m-%d".
        :return: A filtered collection of the upcoming events.
        :rtype: `DataEventCollection`
        """
        if before is not None:
            before = DateUtil.fromStr(before,dateFormat).timestamp
        if after is not None:
            after = DateUtil.fromStr(after,dateFormat).timestamp
        now = DateUtil.now().timestamp
        return self.filter(lambda ev: ev.startDateTimestamp > now and (before is None or ev.startDateTimestamp < before) and (after is None or ev.startDateTimestamp > after))
    
    def ofTypes(self,*types:Union[str,Sequence[str]]):
        """
        Returns a filtered collection of events of the specified types.
        
        :param types: The types of events to filter.
        :type types: `Union[str,Sequence[str]]`
        :return: A filtered collection of events of the specified types.
        :rtype: `DataEventCollection`
        """
        _types = None
        if isinstance(types[0],Sequence):
            if len(types) > 1:
                LOGGER.warning('Only the first sequence of types will be used.')
            _types = types[0]
        else:
            _types = types
        return self.filter(lambda ev: ev.eventType in _types)
    
    @property
    def raidBattles(self):
        """
        Returns a filtered collection containing only raid battles events.
        
        :return: A filtered collection containing only raid battles events.
        :rtype: `DataEventCollection`
        """
        return self.ofTypes(EventType.RAID_BATTLES)
    
    @property
    def raidHours(self):
        """
        Returns a filtered collection containing only raid hour events.
        
        :return: A filtered collection containing only raid hour events.
        :rtype: `DataEventCollection`
        """
        return self.ofTypes(EventType.RAID_HOUR)
    
    @property
    def spotlightHours(self):
        """
        Returns a filtered collection containing only spotlight hour events.
        
        :return: A filtered collection containing only spotlight hour events.
        :rtype: `DataEventCollection`
        """
        return self.ofTypes(EventType.SPOTLIGHT_HOUR)
    
    def withNameLike(self,name:str):
        """
        Returns a filtered collection containing only events whose name contains the specified string.
        
        :param name: The string to search for in the event names.
        :type name: `str`
        :return: A filtered collection containing only events whose name contains the specified string.
        """
        return self.filter(lambda ev: name.lower() in ev.name.lower())
    
    def featuring(self,*pokemons:Union[str,List[str]],strict=False):
        """
        Returns a filtered collection containing only events featuring the specified pokemons.
        
        :param pokemons: The pokemons to search for in the events.
        :type pokemons: `Union[str,List[str]]`
        :param strict: If `strict` is `True`, the event must feature all of the specified pokemons. If `strict` is `False`, the event must feature at least one of the specified pokemons. Defaults to `False`.
        :type strict: `bool`
        :return: A filtered collection containing only events featuring the specified pokemons.
        :rtype: `DataEventCollection`
        """
        if isinstance(pokemons[0],str):
            if strict:
                return self.filter(lambda ev: ev.eventType in EventType.all() and all(pokemon.upper() in ev.content['featuredPokemons'] for pokemon in pokemons))
            return self.filter(lambda ev: ev.eventType in EventType.all() and any(pokemon.upper() in ev.content['featuredPokemons'] for pokemon in pokemons))
        else:
            if strict:
                return self.filter(lambda ev: ev.eventType in EventType.all() and all(pokemon.upper() in ev.content['featuredPokemons'] for pokemon in pokemons[0]))
            return self.filter(lambda ev: ev.eventType in EventType.all() and any(pokemon.upper() in ev.content['featuredPokemons'] for pokemon in pokemons[0]))
    
    def downloadImgs(self,path:str):
        """
        Downloads the images of each event in the collection to the specified path.
        
        :param path: The path to download the images to.
        :type path: `str`
        """
        LOGGER.info(f"Downloading {len(self)} images...")
        for event in self:
            event.downloadImg(path)
        LOGGER.info(f"Downloaded {len(self)} images.")
    
    def __add__(self, o: object):
        if isinstance(o,DataEventCollection):
            return self.__class__(self.items + o.items)
        else:
            raise TypeError(f"unsupported operand type(s) for +: '{self.__class__.__name__}' and '{o.__class__.__name__}'")
        
    def __sub__(self, o: object):
        if isinstance(o,DataEventCollection):
            return self.__class__([ev for ev in self.items if ev not in o.items])
        else:
            raise TypeError(f"unsupported operand type(s) for -: '{self.__class__.__name__}' and '{o.__class__.__name__}'")
        
    def __and__(self, o: object):
        if isinstance(o,DataEventCollection):
            return self.__class__([ev for ev in self.items if ev in o.items])
        else:
            raise TypeError(f"unsupported operand type(s) for &: '{self.__class__.__name__}' and '{o.__class__.__name__}'")
        
    def __or__(self, o: object):
        if isinstance(o,DataEventCollection):
            return self.__add__(o)
        else:
            raise TypeError(f"unsupported operand type(s) for |: '{self.__class__.__name__}' and '{o.__class__.__name__}'")
        
    def __xor__(self, o: object):
        if isinstance(o,DataEventCollection):
            return DataEventCollection([ev for ev in self.items if ev not in o.items] + [ev for ev in o.items if ev not in self.items])
        else:
            raise TypeError(f"unsupported operand type(s) for ^: '{self.__class__.__name__}' and '{o.__class__.__name__}'")
        
    def __radd__(self, o: object):
        if isinstance(o,DataEventCollection):
            return self + o
        else:
            raise TypeError(f"unsupported operand type(s) for +=: '{o.__class__.__name__}' and '{self.__class__.__name__}'")
        
    def __rsub__(self, o: object):
        if isinstance(o,DataEventCollection):
            return self - o
        else:
            raise TypeError(f"unsupported operand type(s) for -=: '{o.__class__.__name__}' and '{self.__class__.__name__}'")
    
    def __rand__(self, o: object):
        if isinstance(o,DataEventCollection):
            return self & o
        else:
            raise TypeError(f"unsupported operand type(s) for &=: '{o.__class__.__name__}' and '{self.__class__.__name__}'")
        
    def __ror__(self, o: object):
        if isinstance(o,DataEventCollection):
            return self | o
        else:
            raise TypeError(f"unsupported operand type(s) for |=: '{o.__class__.__name__}' and '{self.__class__.__name__}'")
        
    def __rxor__(self, o: object):
        if isinstance(o,DataEventCollection):
            return self ^ o
        else:
            raise TypeError(f"unsupported operand type(s) for ^=: '{o.__class__.__name__}' and '{self.__class__.__name__}'")
    
    def __str__(self) -> str:
        return f'DataEventCollection({super().__str__()})'
    
    def __repr__(self) -> str:
        return f'DataEventCollection({super().__repr__()})'