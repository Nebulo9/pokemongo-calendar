from datetime import datetime, timedelta

PROCESSING_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
OUTPUT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

TZ = None
LOCAL_TZ = datetime.now().astimezone().tzinfo
class DateUtil:
    """
    Provides utility methods for working with dates and timestamps in Python.
    """
    
    def __init__(self,date:datetime) -> None:
        self.__date = date
        
    @classmethod
    def fromStr(cls,s:str,format=PROCESSING_DATE_FORMAT):
        """
        Creates a DateUtil object from a string.
        :param s: the string to parse.
        :type s: `str`
        :param format: the format of the string.
        :type format: `str`
        :return: a DateUtil object.
        :rtype: `DateUtil`
        """
        return cls(datetime.strptime(s,format))
    
    @classmethod
    def fromTimestamp(cls,timestamp,tz=None):
        """
        Creates a DateUtil object from a timestamp.
        :param timestamp: the timestamp.
        :type timestamp: `float`
        :param tz: the timezone of the timestamp.
        :type tz: `datetime.tzinfo`
        :return: a DateUtil object.
        :rtype: `DateUtil`
        """
        return cls(datetime.fromtimestamp(timestamp,tz))
    
    @classmethod
    def now(cls):
        """
        Creates a DateUtil object from the current time.
        :return: a DateUtil object.
        :rtype: `DateUtil`
        """
        return cls(datetime.now())
    
    def __str__(self):
        return self.__date.strftime(OUTPUT_DATE_FORMAT)
    
    @property
    def date(self):
        """
        Returns the datetime object.
        :return: the datetime object.
        :rtype: `datetime`
        """
        return self.__date
    
    @property
    def timestamp(self):
        """
        Returns the timestamp.
        :return: the timestamp.
        :rtype: `float`
        """
        return self.__date.timestamp()
    
    @property
    def timezone(self):
        """
        Returns the timezone.
        :return: the timezone.
        :rtype: `datetime.tzinfo`
        """
        return self.__date.tzinfo
    
    @property
    def toStr(self):
        """
        Returns the string representation of the date.
        :return: the string representation of the date.
        :rtype: `str`
        """
        return str(self)
    
    def __add__(self,other):
        if isinstance(other,timedelta):
            return DateUtil.fromTimestamp(self.timestamp + other.total_seconds(),self.timezone)
        elif isinstance(other,DateUtil):
            return DateUtil.fromTimestamp(self.timestamp + other.timestamp,self.timezone)
        elif isinstance(other,float) or isinstance(other,int):
            return DateUtil.fromTimestamp(self.timestamp + other,self.timezone)
        
    def __sub__(self,other):
        if isinstance(other,timedelta):
            return DateUtil.fromTimestamp(self.timestamp - other.total_seconds(),self.timezone)
        elif isinstance(other,DateUtil):
            return DateUtil.fromTimestamp(self.timestamp - other.timestamp,self.timezone)
        elif isinstance(other,float) or isinstance(other,int):
            return DateUtil.fromTimestamp(self.timestamp - other,self.timezone)
    
    def __iadd__(self,other):
        if isinstance(other,timedelta):
            self.__date += other
        elif isinstance(other,DateUtil):
            self.__date += timedelta(seconds=other.timestamp)
        elif isinstance(other,float) or isinstance(other,int):
            self.__date += timedelta(seconds=other)
        return self
    
    def __isub__(self,other):
        if isinstance(other,timedelta):
            self.__date -= other
        elif isinstance(other,DateUtil):
            self.__date -= timedelta(seconds=other.timestamp)
        elif isinstance(other,float) or isinstance(other,int):
            self.__date -= timedelta(seconds=other)
        return self
    
    def __lt__(self,other):
        if isinstance(other,DateUtil):
            return self.timestamp < other.timestamp
        elif isinstance(other,float) or isinstance(other,int):
            return self.timestamp < other
        elif isinstance(other,timedelta):
            return self.timestamp < other.total_seconds()
    
    def __le__(self,other):
        if isinstance(other,DateUtil):
            return self.timestamp <= other.timestamp
        elif isinstance(other,float) or isinstance(other,int):
            return self.timestamp <= other
        elif isinstance(other,timedelta):
            return self.timestamp <= other.total_seconds()
        
    def __gt__(self,other):
        if isinstance(other,DateUtil):
            return self.timestamp > other.timestamp
        elif isinstance(other,float) or isinstance(other,int):
            return self.timestamp > other
        elif isinstance(other,timedelta):
            return self.timestamp > other.total_seconds()
    
    def __ge__(self,other):
        if isinstance(other,DateUtil):
            return self.timestamp >= other.timestamp
        elif isinstance(other,float) or isinstance(other,int):
            return self.timestamp >= other
        elif isinstance(other,timedelta):
            return self.timestamp >= other.total_seconds()
    
    def __eq__(self,other):
        if isinstance(other,DateUtil):
            return self.timestamp == other.timestamp
        elif isinstance(other,float) or isinstance(other,int):
            return self.timestamp == other
        elif isinstance(other,timedelta):
            return self.timestamp == other.total_seconds()
    
    def __ne__(self,other):
        if isinstance(other,DateUtil):
            return self.timestamp != other.timestamp
        elif isinstance(other,float) or isinstance(other,int):
            return self.timestamp != other
        elif isinstance(other,timedelta):
            return self.timestamp != other.total_seconds()
        
    def __repr__(self):
        return f'DateUtil({self.timestamp})'
    
    def __hash__(self):
        return hash(self.timestamp)
    
    def __bool__(self):
        return True